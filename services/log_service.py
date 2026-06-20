from services.db import logs_collection
from datetime import datetime


def create_log(
    user_id,
    username,
    operation,
    file_type,
    file_name=None,
    status="Success",
    file_size=None,
):

    logs_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "operation": operation,
        "file_type": file_type,
        "file_name": file_name,
        "status": status,
        "file_size": file_size,
        "timestamp": datetime.utcnow()
    })
