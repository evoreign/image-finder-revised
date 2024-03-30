from flask import Flask, request, jsonify
import cv2
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import bson.binary
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model
from pymongo import MongoClient
from flask import jsonify
app = Flask(__name__)

# Load the ResNet50 model
base_model = ResNet50(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["attachment-images"]

# Function to extract embeddings from an image
def extract_embedding(image):
    # Preprocess the image
    x = np.expand_dims(image, axis=0)
    x = preprocess_input(x)
    
    # Use ResNet50 to extract features
    features = model.predict(x)
    
    # Flatten the features and convert them to bytes
    return bson.binary.Binary(features.flatten().tobytes())

# Function to find similar images based on embeddings
def find_similar_images(embedding, limit=10):
    similar_images = []
    embedding = np.frombuffer(embedding, dtype=np.float32)  # Convert embedding to float32 array
    for document in collection.find({}, {"_id": 0, "cloudinary.secure_url": 1, "Embeddings": 1}).limit(limit):
        document_embedding = np.frombuffer(document["Embeddings"], dtype=np.float32)  # Convert document_embedding to float32 array
        similarity = np.dot(embedding, document_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(document_embedding))
        similar_images.append({"url": document["cloudinary"]["secure_url"], "similarity": similarity})
    
    similar_images.sort(key=lambda x: x["similarity"], reverse=True)
    return similar_images

@app.route('/find_similar', methods=['POST'])
def find_similar():
    # Get the uploaded image from the request
    file = request.files['image']
    
    # Convert the image to a numpy array
    image_array = np.frombuffer(file.read(), np.uint8)
    
    # Decode the image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Resize the image to the expected shape
    image = keras_image.smart_resize(image, (224, 224))
    
    # Extract the embedding from the uploaded image
    embedding = extract_embedding(image)
    
    # Find similar images based on the embedding
    similar_images = find_similar_images(embedding)
    
    # Convert similarity scores to regular Python floats
    similar_images_json = [
        {"url": item["url"], "similarity": float(item["similarity"])}
        for item in similar_images
    ]
    
    return jsonify(similar_images_json)

if __name__ == '__main__':
    app.run(debug=True)