from flask import Blueprint, jsonify
from services.db import logs_collection

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats/<user_id>", methods=["GET"])
def get_dashboard_stats(user_id):

    try:

        total_encodes = logs_collection.count_documents(
            {"user_id": user_id, "operation": "encode"}
        )

        total_decodes = logs_collection.count_documents(
            {"user_id": user_id, "operation": "decode"}
        )

        images_processed = logs_collection.count_documents(
            {"user_id": user_id, "file_type": "image"}
        )

        audio_processed = logs_collection.count_documents(
            {"user_id": user_id, "file_type": "audio"}
        )

        video_processed = logs_collection.count_documents(
            {"user_id": user_id, "file_type": "video"}
        )

        recent_logs = list(
            logs_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(10)
        )

        print("\n===== RECENT LOGS =====")
        for log in recent_logs:
            print(log)

        activities = []

        for log in recent_logs:
            activities.append(
                {
                    "operation": log.get("operation", "unknown"),
                    "file_type": log.get("file_type", "unknown"),
                    "timestamp": str(log.get("timestamp", "")),
                }
            )

        return jsonify(
            {
                "success": True,
                "total_encodes": total_encodes,
                "total_decodes": total_decodes,
                "images_processed": images_processed,
                "audio_processed": audio_processed,
                "video_processed": video_processed,
                "activities": activities,
            }
        )

    except Exception as e:
        print("DASHBOARD ERROR:", e)

        import traceback

        traceback.print_exc()

        return jsonify({"success": False, "message": str(e)}), 500
