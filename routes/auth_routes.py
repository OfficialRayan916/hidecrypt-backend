print("✅ AUTH_ROUTES FILE LOADED")

from flask import Blueprint, request, jsonify
from services.db import users_collection
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
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        result = users_collection.insert_one({
          "username": username,
          "email": email,
          "password": hashed_password.decode("utf-8"),
          "role": "user"
        })

        print(f"✅ User registered: {email}")

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        print(f"❌ Register Error: {str(e)}")
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "message": "Server error during registration"
        }), 500


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST", "OPTIONS"])
def login():

    print("🔥 LOGIN FUNCTION ENTERED")
    print("METHOD:", request.method)

    if request.method == "GET":
        return jsonify({
            "message": "Login route exists"
        }), 200

    if request.method == "OPTIONS":
        return "", 200

    try:
        print("📍 Login route hit")

        data = request.get_json()
        print(f"📍 Data received: {data}")

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        print(f"📍 Searching for user: {email}")

        user = users_collection.find_one({
            "email": email
        })

        if not user:
            print(f"❌ User not found: {email}")

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        print(f"✅ User found: {user['username']}")
        print("📍 Verifying password...")

        stored_password = user["password"]

        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")

        password_match = bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password
        )

        if not password_match:
            print("❌ Password incorrect")

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        print(f"✅ Login successful: {email}")

        return jsonify({
          "success": True,
          "message": "Login successful",
          "user_id": str(user["_id"]),
          "username": user["username"],
          "email": user["email"],
          "role": user.get("role", "user")
         }), 200

    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "message": "Server error during login"
        }), 500