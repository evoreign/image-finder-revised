import pymongo

def create_capped_collection(database_name, collection_name, max_documents):
    # Connect to MongoDB (adjust connection details as needed)
    client = pymongo.MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client[database_name]

    # Create a capped collection
    db.create_collection(collection_name, capped=True, size=1048576, max=max_documents)

    print(f"Created capped collection '{collection_name}' with max document count: {max_documents}")

if __name__ == "__main__":
    # Specify your database name, collection name, and max document count
    db_name = "test"
    coll_name = "image-queue"
    max_docs = 100

    create_capped_collection(db_name, coll_name, max_docs)
