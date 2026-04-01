import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def initialize_firebase():
    """Initializes Firebase Admin SDK with credentials file."""
    try:
        # Check if serviceAccountKey.json exists
        cred_path = os.path.join(os.getcwd(), 'serviceAccountKey.json')
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Firebase initialized successfully with credentials file.")
            return db
        else:
            print("WARNING: serviceAccountKey.json not found. Operating in local mode (simulated data).")
            return None
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

# Simple mock database for local mode
class MockDB:
    def __init__(self):
        self.quizzes = {}
        self.results = {}
        self.leaderboards = {}

    def collection(self, name):
        return MockCollection(name, self)

class MockCollection:
    def __init__(self, name, db):
        self.name = name
        self.db = db

    def add(self, data):
        # Implementation of Firestore .add()
        import uuid
        doc_id = str(uuid.uuid4())
        if self.name == 'quizzes':
            self.db.quizzes[doc_id] = data
        elif self.name == 'results':
            self.db.results[doc_id] = data
        return MockDocumentReference(doc_id)

    def document(self, doc_id):
        return MockDocumentReference(doc_id, self.db, self.name)

    def stream(self):
        # Implementation for listing all docs
        data_source = {}
        if self.name == 'quizzes':
            data_source = self.db.quizzes
        elif self.name == 'results':
            data_source = self.db.results
        
        return [MockDocumentSnapshot(k, v) for k, v in data_source.items()]

class MockDocumentReference:
    def __init__(self, id, db=None, collection_name=None):
        self.id = id
        self.db = db
        self.collection_name = collection_name

    def get(self):
        if self.db and self.collection_name:
            data = {}
            if self.collection_name == 'quizzes':
                data = self.db.quizzes.get(self.id)
            return MockDocumentSnapshot(self.id, data)
        return None
    
    def set(self, data, merge=False):
        if self.db and self.collection_name:
             if self.collection_name == 'quizzes':
                self.db.quizzes[self.id] = data
             elif self.collection_name == 'results':
                self.db.results[self.id] = data

class MockDocumentSnapshot:
    def __init__(self, id, data):
        self.id = id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data

db = initialize_firebase() or MockDB()
