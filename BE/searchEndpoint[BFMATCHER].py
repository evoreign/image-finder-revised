import logging
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
import uuid
import hashlib

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to generate a unique identifier (UUID) for an image
def generate_image_uuid(image_binary):
    logger.debug("Generating UUID for image...")
    seed = image_binary[:20]
    sha1_hash = hashlib.sha1(seed).digest()
    truncated_hash = sha1_hash[:16]
    uuid_seed = uuid.UUID(bytes=truncated_hash)
    logger.debug(f"UUID generated: {uuid_seed}")
    return str(uuid_seed)

def test_mongodb_connection():
    logger.debug("Testing MongoDB connection...")
    try:
        client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client.test
        db.command("ping")
        logger.debug("MongoDB connection successful.")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

def perform_search(image_to_search):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors for the image to search
    keypoints_to_search, descriptors_to_search = sift.detectAndCompute(image_to_search, None)

    # Create a dictionary to store similarity scores for each reference image
    similarity_scores = {}

    # Connect to MongoDB
    client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]
    collection = db["attachment-images-sifts"]

    # Initialize BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    # Iterate through each MongoDB document
    for doc in collection.find():
        # Check if "Embeddings" key exists and is not None
        if "Embeddings" in doc and doc["Embeddings"] is not None:
            descriptors_reference = np.frombuffer(doc["Embeddings"], dtype=np.float32).reshape(-1, 128)
            matches = bf.match(descriptors_to_search, descriptors_reference)
            matches = sorted(matches, key=lambda x: x.distance)
            similarity_scores[doc["_id"]] = {
                'similarity_score': len(matches),
                'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
            }
        else:
            similarity_scores[doc["_id"]] = {
                'similarity_score': 0,
                'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
            }

    sorted_reference_images = sorted(similarity_scores.values(), key=lambda x: x['similarity_score'], reverse=True)
    return sorted_reference_images

@app.route('/', methods=['GET'])
def check_mongodb_connection():
    logger.debug("Checking MongoDB connection...")
    if test_mongodb_connection():
        return jsonify({'status': 'Connection to MongoDB successful.'}), 200
    else:
        return jsonify({'status': 'Connection to MongoDB failed.'}), 500

@app.route('/search', methods=['POST'])
def search():
    logger.debug("Received search request...")
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400

    file = request.files['image']

    if not isinstance(file, FileStorage):
        return jsonify({'error': 'Invalid image.'}), 400

    file_content = file.read()
    logger.debug("Image file read.")

    image_uuid = str(generate_image_uuid(file_content))
    logger.debug(f"Generated UUID for image: {image_uuid}")

    image = Image.open(io.BytesIO(file_content)).convert('L')
    image_to_search = np.array(image)
    logger.debug("Image converted to grayscale and numpy array.")

    logger.debug("Performing image search...")

    cache_key = 'sorted_reference_images_' + str(hash(file_content))
    cached_result = cache.get(cache_key)
    if cached_result is None:
        sorted_reference_images = perform_search(image_to_search)
        cache.set(cache_key, sorted_reference_images, timeout=600)
    else:
        sorted_reference_images = cached_result

    top_images = sorted_reference_images[:30]

    page = int(request.args.get('page', 1))
    images_per_page = 10
    skip = (page - 1) * images_per_page
    paginated_images = top_images[skip:skip + images_per_page]

    total_pages = len(top_images) // images_per_page
    if len(top_images) % images_per_page > 0:
        total_pages += 1

    return jsonify({
        'sorted_reference_images': paginated_images,
        'current_page': page,
        'total_pages': total_pages,
        'image_uuid': image_uuid,
        'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    })

if __name__ == '__main__':
    app.run(debug=True, port=6000)