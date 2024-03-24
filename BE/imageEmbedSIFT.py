import cv2
import os
import time

# Change the current working directory to the root folder
root_folder = 'C://Users//EdbertKhovey//Documents//Btech image finder revised//BE'
os.chdir(root_folder)

# Load the image to search
image_to_search = cv2.imread('./SampleImage/Ref3-test-crop.png', cv2.IMREAD_GRAYSCALE)

# Initialize SIFT detector
sift = cv2.SIFT_create()

# Detect keypoints and compute descriptors for the image to search
keypoints_to_search, descriptors_to_search = sift.detectAndCompute(image_to_search, None)

# Create a dictionary to store similarity scores for each reference image
similarity_scores = {}

# Get a list of reference image filenames
reference_images_folder = './SampleImage/ref'
reference_image_filenames = os.listdir(reference_images_folder)

# Start timing
start_time = time.time()

# Iterate through each reference image
for filename in reference_image_filenames:
    # Load the reference image
    reference_image_path = os.path.join(reference_images_folder, filename)
    reference_image = cv2.imread(reference_image_path, cv2.IMREAD_GRAYSCALE)
    
    # Detect keypoints and compute descriptors for the reference image
    keypoints_reference, descriptors_reference = sift.detectAndCompute(reference_image, None)
    
    # Match the descriptors between the image to search and the reference image
    matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
    matches = matcher.knnMatch(descriptors_to_search, descriptors_reference, k=2)
    
    # Apply ratio test to find good matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)
    
    # Store the similarity score for this reference image
    similarity_scores[filename] = len(good_matches)

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