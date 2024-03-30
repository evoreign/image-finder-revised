import cv2
import pymongo
from pymongo import MongoClient
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import bson.binary
import cloudinary
from cloudinary import uploader
import time
import pickle
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model

# Load the ResNet50 model
base_model = ResNet50(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)

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
collection = db["attachment-images"]

# Function to extract embeddings from an image
def extract_embedding(image_path):
    # Load the image
    img = keras_image.load_img(image_path, target_size=(224, 224))
    
    # Convert the image to a numpy array and preprocess it
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    # Use ResNet50 to extract features
    features = model.predict(x)
    
    # Flatten the features and convert them to bytes
    return bson.binary.Binary(features.flatten().tobytes())


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
    return cloudinary_response, upload_time


# Folder containing reference images
reference_images_folder = './all image'
reference_image_filenames = os.listdir(reference_images_folder)

# Iterate through each reference image
for filename in reference_image_filenames:
    reference_image_path = os.path.join(reference_images_folder, filename)
    embedding = extract_embedding(reference_image_path)

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
            # Example version as ImageID
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

        # Upload document to MongoDB Atlas
        collection.insert_one(document)
        print(f"Uploaded embedding and Cloudinary data for {
              filename} in {upload_time} seconds")
    else:
        print(f"Embedding for {filename} already exists, skipping.")

print("Upload complete.")
