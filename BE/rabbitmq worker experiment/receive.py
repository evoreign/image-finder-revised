import pickle
import pika
import cv2
import numpy as np
import time
import uuid
from pymongo import MongoClient
import hashlib
from bson import Binary

def generate_uuid(image_data):
    seed = image_data[:20]
    sha1_hash = hashlib.sha1(seed).digest()
    truncated_hash = sha1_hash[:16]
    return(uuid.UUID(bytes=truncated_hash))

def perform_search(task_uuid, image_to_search, uuid_binary, result_collection):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors for the image to search
    keypoints_to_search, descriptors_to_search = sift.detectAndCompute(image_to_search, None)

    # Create a dictionary to store similarity scores for each reference image
    similarity_scores = {}

    # Connect to MongoDB for fetching reference images
    client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]
    reference_collection = db["attachment-images-sifts"]

    # Get a list of MongoDB documents (reference images)
    mongodb_documents = reference_collection.find()

    # Start timing
    start_time = time.time()

    # Initialize BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    # Iterate through each MongoDB document (reference image)
    for doc in mongodb_documents:
        # Check if "Embeddings" key exists and is not None
        if "Embeddings" in doc and doc["Embeddings"] is not None:
            # Load the reference descriptors
            descriptors_reference = np.frombuffer(doc["Embeddings"], dtype=np.float32).reshape(-1, 128)
            
            # Match the descriptors between the image to search and the reference image
            matches = bf.match(descriptors_to_search, descriptors_reference)
            
            # Sort matches by distance
            matches = sorted(matches, key = lambda x:x.distance)
            
            # Store the similarity score, original_filename, and secure_url for this reference image
            similarity_scores[doc["_id"]] = {
                'similarity_score': len(matches),
                'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
            }
        else:
            # Handle the case where "Embeddings" key is missing or None
            similarity_scores[doc["_id"]] = {
                'similarity_score': 0,
                'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
            }

    # Stop timing
    end_time = time.time()

    # Calculate the total execution time
    execution_time = end_time - start_time

    # Sort the reference images based on similarity scores (descending order)
    sorted_reference_images = sorted(similarity_scores.values(), key=lambda x: x['similarity_score'], reverse=True)

    # Store the search results in the specified result collection
    store_search_results(sorted_reference_images, execution_time, uuid_binary, result_collection)

def store_search_results(search_results, execution_time, uuid_binary, result_collection):
    # Connect to MongoDB for storing search results
    client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]

    # Check if the UUID already exists in the image-queue collection
    if result_collection.count_documents({"uuid": uuid_binary}) > 0:
        print(f"UUID {uuid_binary} already exists in the image-queue collection. Skipping storage.")
        return

    # Prepare the data to be inserted into MongoDB
    data = {
        'uuid': uuid_binary,
        'search_results': search_results,
        'execution_time': execution_time,
        'timestamp': time.time()
    }

    # Insert the data into the specified result collection
    result_collection.insert_one(data)

def callback(ch, method, properties, body):
    # Deserialize the task
    task = pickle.loads(body)

    # Retrieve the UUID and BSON Binary representation from the task
    task_uuid = task['uuid']
    uuid_binary = task['uuid_binary']

    # Print the received task UUID
    print(f"Received task with UUID: {task_uuid}")

    # Connect to MongoDB for storing search results
    client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]
    result_collection = db["image-queue"]

    # Check if the UUID already exists in the image-queue collection
    if result_collection.count_documents({"uuid": uuid_binary}) > 0:
        print(f"UUID {uuid_binary} already exists in the image-queue collection. Skipping search.")
        # Acknowledge the task
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Task with UUID {task_uuid} skipped")
        return

    print("Processing task... Please wait....👍")

    # Perform the image similarity search and store results
    image_data = task['image_data']
    image_to_search = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    perform_search(task_uuid, image_to_search, uuid_binary, result_collection)

    # Acknowledge the task
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Task with UUID {task_uuid} completed")

def consume_tasks():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_similarity_tasks')

    # Set QoS prefetch count to 1 to ensure fair dispatching
    channel.basic_qos(prefetch_count=1)

    # Set up callback function for incoming messages
    channel.basic_consume(queue='image_similarity_tasks', on_message_callback=callback)

    print('Worker waiting for tasks...')
    channel.start_consuming()

if __name__ == '__main__':
    consume_tasks()
