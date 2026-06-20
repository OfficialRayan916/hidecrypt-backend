from flask import Blueprint, jsonify
from services.db import logs_collection

admin_history_bp = Blueprint("admin_history", __name__)

@admin_history_bp.route("/all-history", methods=["GET"])
def get_all_history():

    logs = list(
        logs_collection.find().sort("timestamp", -1)
    )

    history = []

    for log in logs:
        history.append({
            "id": str(log.get("_id")),
            "user_id": log.get("user_id"),
            "username": log.get("username"),
            "operation": log.get("operation"),
            "file_type": log.get("file_type"),
            "file_name": log.get("file_name", ""),
            "status": log.get("status", "Success"),
            "file_size": log.get("file_size"),
            "timestamp": log.get("timestamp")
        })

    return jsonify({
        "success": True,
        "history": history
    })