"""
MongoDB database configuration and setup for Mergington High School API
"""

try:
    from pymongo import MongoClient
    from argon2 import PasswordHasher
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1000)
    # Test connection
    client.admin.command('ping')
    db = client['mergington_high']
    activities_collection = db['activities']
    teachers_collection = db['teachers']
    USING_MOCK = False
except Exception as e:
    print(f"MongoDB not available, using mock database: {e}")
    from .mock_database import mock_activities_collection, mock_teachers_collection, init_mock_database
    
    activities_collection = mock_activities_collection
    teachers_collection = mock_teachers_collection
    USING_MOCK = True

# Import initial data
from .initial_data import initial_activities, initial_teachers, hash_password

def init_database():
    """Initialize database if empty"""
    
    if USING_MOCK:
        # Initialize mock database
        init_mock_database()
        return

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

