from flask import Blueprint, request, jsonify
from bson import ObjectId
from services.db import users_collection

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile/<user_id>", methods=["GET"])
def get_profile(user_id):
    try:

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify(
            {
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "area": user.get("area", ""),
                "profile_photo": user.get("profile_photo", ""),
                "userId": str(user["_id"]),
            }
        )

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@profile_bp.route("/profile/update", methods=["PUT"])
def update_profile():

    try:

        data = request.json

        user_id = data["user_id"]

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "area": data.get("area", ""),
                    "profile_photo": data.get("profile_photo", ""),
                }
            },
        )

        return jsonify({"success": True, "message": "Profile updated successfully"})

    except Exception as e:
        return jsonify({"message": str(e)}), 500
