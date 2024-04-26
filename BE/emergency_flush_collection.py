from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient(
    "mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["image-queue"]

# Ask for user confirmation
print("WARNING: You are about to delete all documents in the collection. This action cannot be undone.")
confirmation = input("Are you sure you want to continue? (y/n): ")

if confirmation.lower() == 'y':
    # Delete all documents in the collection
    result = collection.delete_many({})

    print(f"Deleted {result.deleted_count} documents.")
else:
    print("Operation cancelled.")