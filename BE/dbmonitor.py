from pymongo import MongoClient

def get_mongodb_stats():
    # Connect to MongoDB
    client = MongoClient('mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    
    # Get the admin database for serverStatus command
    db = client.admin
    
    # Run serverStatus command to get server stats
    server_status = db.command("serverStatus")
    
    # Extract active connections and other stats
    active_connections = server_status['connections']['current']
    # Add more stats as needed
    # Example: total_documents = server_status['metrics']['document']['inserted']
    
    # Close the connection
    client.close()
    
    return {
        'active_connections': active_connections,
        # Add other stats to return
    }

if __name__ == "__main__":
    stats = get_mongodb_stats()
    print("MongoDB Stats:")
    print(f"Active Connections: {stats['active_connections']}")
    # Print other stats as needed
