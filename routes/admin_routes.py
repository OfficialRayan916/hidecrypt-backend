from flask import Blueprint, jsonify
from services.db import users_collection, logs_collection
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard/admin-stats", methods=["GET"])
def get_admin_stats():

    total_users = users_collection.count_documents({})

    total_encodes = logs_collection.count_documents({
        "operation": "encode"
    })

    total_decodes = logs_collection.count_documents({
        "operation": "decode"
    })

    active_sessions = total_users

    image_count = logs_collection.count_documents({
        "file_type": "image"
    })

    audio_count = logs_collection.count_documents({
        "file_type": "audio"
    })

    video_count = logs_collection.count_documents({
        "file_type": "video"
    })

    # ==========================
    # Recent Activities
    # ==========================
    recent_logs = list(
        logs_collection.find()
        .sort("timestamp", -1)
        .limit(10)
    )

    activities = []

    for log in recent_logs:
        activities.append({
            "user": log.get("username", "Unknown"),
            "email": "",
            "operation": log.get("operation", ""),
            "file_type": log.get("file_type", ""),
            "status": log.get("status", "success").lower(),
            "timestamp": log.get("timestamp")
        })

    # ==========================
    # Real Daily Activity (7 Days)
    # ==========================
    daily_activity = []

    for i in range(6, -1, -1):

        day = datetime.utcnow() - timedelta(days=i)

        start = datetime(
            day.year,
            day.month,
            day.day
        )

        end = start + timedelta(days=1)

        encode_count = logs_collection.count_documents({
            "operation": "encode",
            "timestamp": {
                "$gte": start,
                "$lt": end
            }
        })

        decode_count = logs_collection.count_documents({
            "operation": "decode",
            "timestamp": {
                "$gte": start,
                "$lt": end
            }
        })

        daily_activity.append({
            "day": day.strftime("%a"),
            "encode": encode_count,
            "decode": decode_count
        })

    return jsonify({
        "success": True,

        "total_users": total_users,
        "total_encodes": total_encodes,
        "total_decodes": total_decodes,
        "active_sessions": active_sessions,

        "delta_users": 0,
        "delta_encodes": 0,
        "delta_decodes": 0,
        "delta_sessions": 0,

        "images_processed": image_count,
        "audio_processed": audio_count,
        "video_processed": video_count,

        "daily_activity": daily_activity,

        "activities": activities
    })