import pickle
import pika
import cv2
import numpy as np
import time
import uuid
from pymongo import MongoClient
import hashlib
from bson import Binary
import psutil

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

    # Initialize FLANN matcher
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Iterate through each MongoDB document (reference image)
    for doc in mongodb_documents:
        # Check if "Embeddings" key exists and is not None or 0
        if "Embeddings" in doc and doc["Embeddings"] not in (None, 0):
            # Load the reference descriptors
            descriptors_reference = np.frombuffer(doc["Embeddings"], dtype=np.float32).reshape(-1, 128)

            # Check if reference descriptors are not empty
            if descriptors_reference.size > 0:
                # Match the descriptors between the image to search and the reference image
                matches = flann.knnMatch(descriptors_to_search, descriptors_reference, k=1)

                # Apply ratio test to filter good matches
                good_matches = []
                for m in matches:
                    if len(m) > 0:
                        good_matches.append(m[0])

                # Store the similarity score, original_filename, and secure_url for this reference image
                similarity_scores[doc["_id"]] = {
                    'similarity_score': len(good_matches),
                    'original_filename': doc['cloudinary']['original_filename'] if 'cloudinary' in doc and 'original_filename' in doc['cloudinary'] else None,
                    'secure_url': doc['cloudinary']['secure_url'] if 'cloudinary' in doc and 'secure_url' in doc['cloudinary'] else None
                }
        else:
            # Skip the document if "Embeddings" key is missing, None, or 0
            continue

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

def monitor_resources(interval=60):
    while True:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)

        # Get memory usage
        mem = psutil.virtual_memory()
        mem_percent = mem.percent

        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        # Log resource usage metrics
        log_metrics(cpu_percent, mem_percent, disk_percent)

        # Wait for the specified interval
        time.sleep(interval)

def log_metrics(cpu_percent, mem_percent, disk_percent):
    # Write resource usage metrics to a log file
    with open('resource_usage.log', 'a') as f:
        f.write(f"Time:{time.time()} CPU Usage: {cpu_percent}% | Memory Usage: {mem_percent}% | Disk Usage: {disk_percent}%\n")

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
    # Start resource monitoring in a separate thread
    import threading
    resource_monitor_thread = threading.Thread(target=monitor_resources)
    resource_monitor_thread.daemon = True
    resource_monitor_thread.start()

    # Start consuming tasks
    consume_tasks()
