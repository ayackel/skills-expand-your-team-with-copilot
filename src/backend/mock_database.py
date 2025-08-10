"""
Mock MongoDB collections for testing without MongoDB server
"""

import copy
from .initial_data import initial_activities, initial_teachers

class MockCollection:
    """Mock MongoDB collection that stores data in memory"""
    
    def __init__(self, data=None):
        self.data = data or {}
    
    def find(self, query=None):
        """Mock find method"""
        if query is None:
            query = {}
        
        # Simple query processing for basic cases
        results = []
        for doc_id, doc_data in self.data.items():
            doc = copy.deepcopy(doc_data)
            doc['_id'] = doc_id
            
            # Check if document matches query
            if self._matches_query(doc, query):
                results.append(doc)
        
        return results
    
    def find_one(self, query):
        """Mock find_one method"""
        if isinstance(query, dict) and '_id' in query:
            doc_id = query['_id']
            if doc_id in self.data:
                doc = copy.deepcopy(self.data[doc_id])
                doc['_id'] = doc_id
                return doc
        return None
    
    def count_documents(self, query=None):
        """Mock count_documents method"""
        return len(self.data)
    
    def insert_one(self, document):
        """Mock insert_one method"""
        doc_id = document.get('_id')
        if doc_id:
            doc_copy = copy.deepcopy(document)
            doc_copy.pop('_id')
            self.data[doc_id] = doc_copy
        return MockResult(modified_count=1)
    
    def update_one(self, filter_query, update_query):
        """Mock update_one method"""
        doc_id = filter_query.get('_id')
        if doc_id and doc_id in self.data:
            doc = self.data[doc_id]
            
            # Handle $push operation
            if '$push' in update_query:
                for field, value in update_query['$push'].items():
                    if field in doc:
                        doc[field].append(value)
                    else:
                        doc[field] = [value]
                return MockResult(modified_count=1)
            
            # Handle $pull operation
            if '$pull' in update_query:
                for field, value in update_query['$pull'].items():
                    if field in doc and isinstance(doc[field], list):
                        if value in doc[field]:
                            doc[field].remove(value)
                return MockResult(modified_count=1)
        
        return MockResult(modified_count=0)
    
    def aggregate(self, pipeline):
        """Mock aggregate method - basic implementation"""
        # This is a simplified implementation for the days aggregation
        # In reality, MongoDB aggregation is much more complex
        if (len(pipeline) == 3 and 
            pipeline[0].get('$unwind') == '$schedule_details.days' and
            '$group' in pipeline[1] and
            '$sort' in pipeline[2]):
            
            # Extract all unique days
            days_set = set()
            for doc_data in self.data.values():
                if 'schedule_details' in doc_data and 'days' in doc_data['schedule_details']:
                    for day in doc_data['schedule_details']['days']:
                        days_set.add(day)
            
            # Return in the expected format
            return [{'_id': day} for day in sorted(days_set)]
        
        return []
    
    def _matches_query(self, doc, query):
        """Simple query matching logic"""
        if not query:
            return True
        
        for field, condition in query.items():
            # Handle nested field queries
            if '.' in field:
                parts = field.split('.')
                current = doc
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                
                final_field = parts[-1]
                if final_field not in current:
                    return False
                
                field_value = current[final_field]
            else:
                if field not in doc:
                    return False
                field_value = doc[field]
            
            # Handle different query operators
            if isinstance(condition, dict):
                for operator, value in condition.items():
                    if operator == '$in':
                        if not any(item in field_value for item in value):
                            return False
                    elif operator == '$gte':
                        if field_value < value:
                            return False
                    elif operator == '$lte':
                        if field_value > value:
                            return False
            else:
                if field_value != condition:
                    return False
        
        return True

class MockResult:
    """Mock result object for update operations"""
    
    def __init__(self, modified_count=0):
        self.modified_count = modified_count

# Initialize mock collections
mock_activities_collection = MockCollection()
mock_teachers_collection = MockCollection()

def init_mock_database():
    """Initialize mock database with sample data"""
    # Initialize activities
    for name, details in initial_activities.items():
        mock_activities_collection.insert_one({"_id": name, **details})
    
    # Initialize teachers
    for teacher in initial_teachers:
        mock_teachers_collection.insert_one({"_id": teacher["username"], **teacher})