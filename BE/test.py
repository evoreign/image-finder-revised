import cv2
import os
import time
from pymongo import MongoClient
import numpy as np
# Change the current working directory to the root folder
root_folder = 'C://Users//EdbertKhovey//Documents//Btech image finder revised//BE'
os.chdir(root_folder)

# Load the image to search
image_to_search = cv2.imread('./SampleImage/656.png', cv2.IMREAD_GRAYSCALE)

# Initialize SIFT detector
sift = cv2.SIFT_create()

# Detect keypoints and compute descriptors for the image to search
keypoints_to_search, descriptors_to_search = sift.detectAndCompute(image_to_search, None)

# Create a dictionary to store similarity scores for each reference image
similarity_scores = {}

# Connect to MongoDB
client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]  # replace with your database name
collection = db["attachment-images"]  # replace with your collection name

# Get a list of MongoDB documents
mongodb_documents = collection.find()

# Start timing
start_time = time.time()

# Iterate through each MongoDB document
for doc in mongodb_documents:
    # Check if "Embeddings" key exists and is not None
    if "Embeddings" in doc and doc["Embeddings"] is not None:
        # Load the reference descriptors
        descriptors_reference = np.frombuffer(doc["Embeddings"], dtype=np.float32).reshape(-1, 128)
        
        # Match the descriptors between the image to search and the reference image
        matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
        matches = matcher.knnMatch(descriptors_to_search, descriptors_reference, k=2)
        
        # Apply ratio test to find good matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
        
        # Store the similarity score for this reference image
        similarity_scores[doc["filename"]] = len(good_matches)
    else:
        # Handle the case where "Embeddings" key is missing or None
        similarity_scores[doc["filename"]] = 0  # Assigning a similarity score of 0

# Stop timing
end_time = time.time()

# Calculate the total execution time
execution_time = end_time - start_time

# Sort the reference images based on similarity scores (descending order)
sorted_reference_images = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

# Print the sorted list of reference images and their similarity scores
for filename, score in sorted_reference_images:
    print(f"Similarity score for {filename}: {score}")

# Print the total execution time
print(f"Total execution time: {execution_time} seconds")