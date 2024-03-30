from flask import Flask, request, jsonify
from flask_caching import Cache
import cv2
import numpy as np
import os
import time
from pymongo import MongoClient
from werkzeug.datastructures import FileStorage
from PIL import Image
import io

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def perform_search(image_to_search):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors for the image to search
    keypoints_to_search, descriptors_to_search = sift.detectAndCompute(image_to_search, None)

    # Create a dictionary to store similarity scores for each reference image
    similarity_scores = {}

    # Connect to MongoDB
    client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]  # replace with your database name
    collection = db["attachment-images-sifts"]  # replace with your collection name

    # Get a list of MongoDB documents
    mongodb_documents = collection.find()

    # Start timing
    start_time = time.time()

    # Initialize BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    # Iterate through each MongoDB document
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
                'similarity_score': 0,  # Assigning a similarity score of 0
                'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
            }

    # Stop timing
    end_time = time.time()

    # Calculate the total execution time
    execution_time = end_time - start_time

    # Sort the reference images based on similarity scores (descending order)
    sorted_reference_images = sorted(similarity_scores.values(), key=lambda x: x['similarity_score'], reverse=True)

    # Return the sorted reference images and execution time
    return sorted_reference_images, execution_time

@app.route('/search', methods=['POST'])
def search():
    # Check if an image was posted
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400

    file = request.files['image']

    if not isinstance(file, FileStorage):
        return jsonify({'error': 'Invalid image.'}), 400

    # Read the file content into a variable
    file_content = file.read()

    # Convert the image to grayscale
    image = Image.open(io.BytesIO(file_content)).convert('L')
    image_to_search = np.array(image)

    # Get the cached results if they exist, otherwise pHWerform the search and cache the results
    cache_key = 'sorted_reference_images_' + str(hash(file_content))
    sorted_reference_images, execution_time = cache.get(cache_key) or perform_search(image_to_search)
    if cache.get(cache_key) is None:
        cache.set(cache_key, (sorted_reference_images, execution_time), timeout=600)

    # Select the top 30 images
    top_images = sorted_reference_images[:30]

    # Get the page number from the request parameters (default to 1 if not provided)
    page = int(request.args.get('page', 1))

    # Define the number of images per page
    images_per_page = 10

    # Calculate the number of images to skip
    skip = (page - 1) * images_per_page

    # Apply pagination on the top images
    paginated_images = top_images[skip:skip + images_per_page]

    # Calculate the total number of pages
    total_pages = len(top_images) // images_per_page
    if len(top_images) % images_per_page > 0:
        total_pages += 1

    # Return the paginated images, the current page number, and the total number of pages as a JSON response
    return jsonify({
        'sorted_reference_images': paginated_images,
        'execution_time': execution_time,
        'current_page': page,
        'total_pages': total_pages
    })

if __name__ == '__main__':
    app.run(debug=True, port=6000)