import cv2
import pymongo
from pymongo import MongoClient
import numpy as np
import bson.binary
import base64
import pickle

# Connect to MongoDB Atlas
client = MongoClient(
    "mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["attachment-images"]

# Function to extract embeddings from an image


def extract_embedding(image_path):
    sift = cv2.SIFT_create()
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    keypoints, descriptors = sift.detectAndCompute(image, None)
    binary_descriptors = bson.binary.Binary(
        descriptors.astype(np.float32).tobytes())
    return binary_descriptors

# Function to compare embeddings using KNN


def compare_embeddings(local_embedding, mongodb_embeddings, k):
    sift = cv2.SIFT_create()
    matches = []

    # Convert local embedding to numpy array
    local_descriptors = np.frombuffer(local_embedding, dtype=np.float32).reshape(-1, 128)

    for doc in mongodb_embeddings:
        mongodb_descriptors = np.frombuffer(doc["Embeddings"], dtype=np.float32).reshape(-1, 128)

        # Create a BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

        # Match descriptors
        match = bf.knnMatch(local_descriptors, mongodb_descriptors, k)

        # Sort matches based on distance
        match = sorted(match, key=lambda x: x.distance)

        matches.append((doc["filename"], match))

    return matches


# Load the local image
local_image_path = './SampleImage/656.png'
local_embedding = extract_embedding(local_image_path)

# Query MongoDB to retrieve all documents containing embeddings
mongodb_embeddings = collection.find({}, {"filename": 1, "Embeddings": 1})

# Compare local embedding with embeddings in MongoDB using KNN
k = 1  # Adjust the number of nearest neighbors as needed
matches = compare_embeddings(local_embedding, mongodb_embeddings, k=k)

# Print the matches
for filename, match in matches:
    print(f"Matches for {filename}: {len(match)}")
    if len(match) > 0:
        # Accessing distances of individual matches
        for m in match:
            print(f"Matched descriptors: {m.distance}")
    else:
        print("No matches found.")

# Optionally, filter the matches or perform additional processing as needed
