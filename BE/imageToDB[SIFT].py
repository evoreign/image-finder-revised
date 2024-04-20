import cv2
import pymongo
from pymongo import MongoClient
import os
import numpy as np
import bson.binary
import cloudinary
from cloudinary import uploader
import time
import pickle

# Configure Cloudinary
cloudinary.config(
    cloud_name="dfqziqcfa",
    api_key="195752977662795",
    api_secret="nSQqLE_vRrLlS098NKR7IGpYCr0"
)

# Change the current working directory to the root folder
root_folder = 'C://Users//EdbertKhovey//Documents//Btech image finder revised//BE'
os.chdir(root_folder)

# Connect to MongoDB Atlas
client = MongoClient(
    "mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["attachment-images-sifts"]

# Function to extract embeddings from an image
def extract_embedding(image_path):
    start_time = time.time()  # Start timing
    sift = cv2.SIFT_create()
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    keypoints, descriptors = sift.detectAndCompute(image, None)
    if descriptors is not None:  # Check if descriptors are not None
        # Ensure that the descriptors are of type float32
        descriptors = descriptors.astype(np.float32)
        # Serialize descriptors to bytes
        embedding = bson.binary.Binary(descriptors.flatten().tobytes())
    else:
        # If no descriptors are found, return None
        embedding = None
    end_time = time.time()  # End timing
    embedding_time = end_time - start_time
    print(f"Extracting embedding for {image_path} took {embedding_time} seconds")
    return embedding, embedding_time

# Function to check if an embedding already exists in the collection
def embedding_exists(embedding):
    existing_embeddings = collection.find({}, {"_id": 0, "Embeddings": 1})
    for existing_embedding in existing_embeddings:
        if existing_embedding["Embeddings"] == embedding:
            return True
    return False

# Function to upload image to Cloudinary and measure time taken
def upload_to_cloudinary(image_path):
    start_time = time.time()  # Start timing
    cloudinary_response = uploader.upload(image_path)
    end_time = time.time()  # End timing
    upload_time = end_time - start_time  # Calculate upload time
    print(f"Uploading {image_path} to Cloudinary took {upload_time} seconds")
    return cloudinary_response, upload_time

# Folder containing reference images
reference_images_folder = './all image'
reference_image_filenames = os.listdir(reference_images_folder)

# Iterate through each reference image
for filename in reference_image_filenames:
    reference_image_path = os.path.join(reference_images_folder, filename)
    embedding, embedding_time = extract_embedding(reference_image_path)

    # Check if embedding already exists in MongoDB Atlas
    if not embedding_exists(embedding):
        # Upload image to Cloudinary and measure time
        cloudinary_response, upload_time = upload_to_cloudinary(
            reference_image_path)

        # Extract relevant Cloudinary data
        cloudinary_data = {
            "public_id": cloudinary_response.get("public_id", ""),
            "original_filename": cloudinary_response.get("original_filename", ""),
            "format": cloudinary_response.get("format", ""),
            "secure_url": cloudinary_response.get("secure_url", ""),
            "resource_type": cloudinary_response.get("resource_type", ""),
        }

        # Get file information
        file_info = os.stat(reference_image_path)
        file_size = file_info.st_size

        # Create MongoDB document
        document = {
            "ImageID": str(cloudinary_response["version"]),
            "Embeddings": embedding,
            "cloudinary": cloudinary_data,
            "filename": filename,
            "mimeType": cloudinary_response.get("format", ""),
            "filesize": file_size,
            "width": cloudinary_response.get("width", ""),
            "height": cloudinary_response.get("height", ""),
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            "__v": 0
        }

        start_time = time.time()  # Start timing
        # Upload document to MongoDB Atlas
        collection.insert_one(document)
        end_time = time.time()  # End timing
        mongodb_time = end_time - start_time
        print(f"Uploading document to MongoDB took {mongodb_time} seconds")
        total_time = embedding_time + upload_time + mongodb_time
        print(f"Total time for {filename}: {total_time} seconds")
    else:
        print(f"Embedding for {filename} already exists, skipping.")

print("Upload complete.")