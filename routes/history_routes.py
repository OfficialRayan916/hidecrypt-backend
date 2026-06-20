from flask import Blueprint, jsonify
from services.db import logs_collection

history_bp = Blueprint("history", __name__)


@history_bp.route("/<user_id>", methods=["GET"])
def get_history(user_id):
    try:

        logs = list(
            logs_collection.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("timestamp", -1)
        )

        return jsonify({
            "success": True,
            "logs": logs
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500