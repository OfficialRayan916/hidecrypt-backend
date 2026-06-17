from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file
from services.image_steganography import (
    encode_message,
    decode_message
)

import os
import uuid

image_bp = Blueprint("image", __name__)

UPLOAD_FOLDER = "uploads"
ENCODED_FOLDER = "encoded"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)


# =========================
# ENCODE
# =========================
@image_bp.route("/encode", methods=["POST"])
def encode():

    try:

        image = request.files.get("image")
        secret_message = request.form.get("message")

        user_id = request.form.get("user_id")
        username = request.form.get("username")
        password = request.form.get("password")

        print("USER ID:", user_id)
        print("USERNAME:", username)

        if not image:
            return jsonify({
                "success": False,
                "message": "Image is required"
            }), 400

        if not secret_message:
            return jsonify({
                "success": False,
                "message": "Secret message is required"
            }), 400

        image_name = f"{uuid.uuid4()}.png"

        input_path = os.path.join(
            UPLOAD_FOLDER,
            image_name
        )

        output_path = os.path.join(
            ENCODED_FOLDER,
            image_name
        )

        image.save(input_path)

        encode_message(
            input_path,
            secret_message,
            output_path,
            password
        )

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="encode",
                file_type="image"
            )

        return send_file(
            output_path,
            as_attachment=True,
            download_name="encoded_image.png"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================
# DECODE
# =========================
@image_bp.route("/decode", methods=["POST"])
def decode():

    try:

        image = request.files.get("image")
        password = request.form.get("password")

        user_id = request.form.get("user_id")
        username = request.form.get("username")

        if not image:
            return jsonify({
                "success": False,
                "message": "Image is required"
            }), 400

        image_name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(
            UPLOAD_FOLDER,
            image_name
        )

        image.save(image_path)

        secret_message = decode_message(
            image_path,
            password
        )

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="decode",
                file_type="image"
            )

        return jsonify({
            "success": True,
            "message": secret_message
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
