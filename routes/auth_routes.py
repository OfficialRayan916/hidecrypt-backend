print("✅ AUTH_ROUTES FILE LOADED")

from flask import Blueprint, request, jsonify
from services.db import users_collection, logs_collection, auth_logs_collection
from datetime import datetime
import bcrypt
import traceback

auth_bp = Blueprint("auth", __name__)


# =========================
# REGISTER
# =========================
@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():

    if request.method == "OPTIONS":
        return "", 200

    try:
        print("📍 Register route hit")

        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return (
                jsonify({"success": False, "message": "All fields are required"}),
                400,
            )

        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            return jsonify({"success": False, "message": "Email already exists"}), 409

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        result = users_collection.insert_one(
            {
                "username": username,
                "email": email,
                "password": hashed_password.decode("utf-8"),
                "role": "user",
                "area": "",
                "profile_photo": "",
            }
        )

        print(f"✅ User registered: {email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "user_id": str(result.inserted_id),
                }
            ),
            201,
        )

    except Exception as e:
        print(f"❌ Register Error: {str(e)}")
        print(traceback.format_exc())

        return (
            jsonify({"success": False, "message": "Server error during registration"}),
            500,
        )


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST", "OPTIONS"])
def login():

    print("🔥 LOGIN FUNCTION ENTERED")
    print("METHOD:", request.method)

    if request.method == "GET":
        return jsonify({"message": "Login route exists"}), 200

    if request.method == "OPTIONS":
        return "", 200

    try:
        print("📍 Login route hit")

        data = request.get_json()
        print(f"📍 Data received: {data}")

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify(
                    {"success": False, "message": "Email and password are required"}
                ),
                400,
            )

        print(f"📍 Searching for user: {email}")

        user = users_collection.find_one({"email": email})

        if not user:
            print(f"❌ User not found: {email}")

            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        print(f"✅ User found: {user['username']}")
        print("📍 Verifying password...")

        stored_password = user["password"]

        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")

        password_match = bcrypt.checkpw(password.encode("utf-8"), stored_password)

        if not password_match:
            print("❌ Password incorrect")

            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        print(f"✅ Login successful: {email}")

        auth_logs_collection.insert_one(
            {
                "user_id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user.get("role", "user"),
                "action": "login",
                "timestamp": datetime.utcnow(),
            }
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user.get("role", "user"),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        print(traceback.format_exc())

        return jsonify({"success": False, "message": "Server error during login"}), 500


@auth_bp.route("/admin-login", methods=["POST"])
def admin_login():

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify(
                    {"success": False, "message": "Email and password are required"}
                ),
                400,
            )

        user = users_collection.find_one({"email": email})

        if not user:
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        stored_password = user["password"]

        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")

        password_match = bcrypt.checkpw(password.encode("utf-8"), stored_password)

        if not password_match:
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        # ADMIN CHECK
        if user.get("role") != "admin":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Access denied. Only admins can login.",
                    }
                ),
                403,
            )

        # LOGIN LOG
        auth_logs_collection.insert_one(
            {
                "user_id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "action": "login",
                "timestamp": datetime.utcnow(),
            }
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Admin login successful",
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                }
            ),
            200,
        )

    except Exception as e:
        print("Admin Login Error:", str(e))

        return (
            jsonify({"success": False, "message": "Server error during admin login"}),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
def logout():

    try:
        data = request.get_json()

        user_id = data.get("user_id")
        username = data.get("username")
        email = data.get("email")
        role = data.get("role")

        print(f"🚪 Logout: {email}")

        auth_logs_collection.insert_one(
            {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "action": "logout",
                "timestamp": datetime.utcnow(),
            }
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Logout logged",
                }
            ),
            200,
        )

    except Exception as e:
        print("Logout Error:", str(e))

        return (
            jsonify(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
            500,
        )


@auth_bp.route("/users", methods=["GET"])
def get_all_users():
    try:

        users = list(
            users_collection.find({}, {"password": 0})  # Don't return password
        )

        user_list = []

        for user in users:

            user_id = str(user["_id"])
            user["_id"] = user_id
            user["user_id"] = user_id

            image_encode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "image", "operation": "encode"}
            )

            image_decode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "image", "operation": "decode"}
            )

            audio_encode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "audio", "operation": "encode"}
            )

            audio_decode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "audio", "operation": "decode"}
            )

            video_encode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "video", "operation": "encode"}
            )

            video_decode = logs_collection.count_documents(
                {"user_id": user_id, "file_type": "video", "operation": "decode"}
            )

            user["image_encode"] = image_encode
            user["image_decode"] = image_decode

            user["audio_encode"] = audio_encode
            user["audio_decode"] = audio_decode

            user["video_encode"] = video_encode
            user["video_decode"] = video_decode

            last_login = auth_logs_collection.find_one(
                {"user_id": user_id, "action": "login"}, sort=[("timestamp", -1)]
            )

            if last_login:
                user["last_login"] = last_login["timestamp"]
            else:
                user["last_login"] = None

            user["total_encode"] = image_encode + audio_encode + video_encode

            user["total_decode"] = image_decode + audio_decode + video_decode

            user_list.append(user)

        return jsonify(user_list), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
