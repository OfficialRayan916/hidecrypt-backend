from services.db import logs_collection
from datetime import datetime


def create_log(
    user_id,
    username,
    operation,
    file_type
):

    logs_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "operation": operation,
        "file_type": file_type,
        "timestamp": datetime.utcnow()
    })
    from services.db import logs_collection


def create_log(
    user_id,
    username,
    operation,
    file_type
):

    logs_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "operation": operation,
        "file_type": file_type,
        "timestamp": datetime.utcnow()
    })

    print("✅ LOG SAVED")
