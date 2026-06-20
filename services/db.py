from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

def get_db():
    MONGO_URI = os.getenv("MONGO_URI")

    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where()
    )

    db = client["hidecrypt"]
    return db

db = get_db()
users_collection = db["users"]
logs_collection = db["logs"]
auth_logs_collection = db["auth_logs"]

print("MongoDB Connected Successfully!")