import pickle
import pika
from flask import Flask, request, jsonify
from PIL import Image
import io
import cv2
import numpy as np
import os
import time
import uuid
from pymongo import MongoClient
import hashlib
from bson import Binary
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
def generate_uuid(image_data):
    seed = image_data[:20]
    sha1_hash = hashlib.sha1(seed).digest()
    truncated_hash = sha1_hash[:16]
    return uuid.UUID(bytes=truncated_hash)
def enqueue_task(task):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_similarity_tasks')

    # Generate UUID based on image data
    task_uuid = generate_uuid(task['image_data'])
    task['uuid'] = str(task_uuid)

    # Convert the UUID to a BSON-compatible representation
    task['uuid_binary'] = Binary.from_uuid(task_uuid)

    # Publish the task to the queue
    channel.basic_publish(exchange='', routing_key='image_similarity_tasks', body=pickle.dumps(task))
    connection.close()

    # Return the UUID as a response
    return jsonify({'UUID': f'{task_uuid}'}), 202

client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]  # Replace with your database name
result_collection = db["image-queue"]
@app.route('/imagesearch/<uuid_str>', methods=['GET'])
def get_search_results(uuid_str):
    try:
        # Try to create a BSON Binary object from the string representation of the UUID
        uuid_binary = Binary.from_uuid(uuid.UUID(uuid_str))
    except ValueError:
        # If the provided UUID is already a BSON Binary object, use it directly
        uuid_binary = uuid_str

    # Query the database to find the document with the given UUID
    result = result_collection.find_one({'uuid': uuid_binary})
    if result:
        # If the document is found, get the search results and UUID
        search_results = result['search_results']
        result_uuid = str(result['uuid'])  # Convert UUID to string

        # Create a list of dictionaries with the search results and the UUID
        search_results_with_uuid = [
            {
                'similarity_score': item['similarity_score'],
                'original_filename': item['original_filename'],
                'secure_url': item['secure_url'],
                'uuid': result_uuid  # Use the same UUID for all search results
            }
            for item in search_results
        ]
        return jsonify(search_results_with_uuid)
    else:
        # If the document is not found, return an error response
        return jsonify({'error': 'Please be patient, your image is in the queue. Check this page periodically'}), 404

@app.route('/search', methods=['POST'])
def search():
    # Check if an image was posted
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
    file = request.files['image']
    if not file:
        return jsonify({'error': 'Invalid image.'}), 400

    # Read the file content into a variable
    image_data = file.read()

    # Get the filename
    filename = file.filename

    # Serialize the task (e.g., image data and filename)
    task = {
        'image_data': image_data,
        'filename': filename
    }

    # Enqueue the task onto RabbitMQ
    response = enqueue_task(task)

    # Return the response from the enqueue_task function
    return response

if __name__ == '__main__':
    app.run(debug=True, port=80)
