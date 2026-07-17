from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file
from services.image_steganography import (
    encode_payload,
    decode_payload,
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
        payload_type = request.form.get("payload_type")

        secret_message = request.form.get("message")

        secret_image = request.files.get("secret_image")

        secret_audio = request.files.get("secret_audio")

        user_id = request.form.get("user_id")

        username = request.form.get("username")

        password = request.form.get("password")

        print("USER ID:", user_id)
        print("USERNAME:", username)

        if not image:
            return jsonify({"success": False, "message": "Image is required"}), 400

        if payload_type == "text" and not secret_message:
            return jsonify({
                "success": False,
                "message": "Secret message is required"
            }), 400

        if payload_type == "image" and not secret_image:
            return jsonify({
                "success": False,
                "message": "Secret image is required"
            }), 400

        if payload_type == "audio" and not secret_audio:
            return jsonify({
                "success": False,
                "message": "Secret audio is required"
            }), 400

        image_name = f"{uuid.uuid4()}.png"

        input_path = os.path.join(UPLOAD_FOLDER, image_name)

        output_path = os.path.join(ENCODED_FOLDER, image_name)

        image.save(input_path)

        file_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)

        if payload_type == "text":

            encode_payload(
                image_path=input_path,
                payload_type="text",
                output_path=output_path,
                password=password,
                text=secret_message
            )

        elif payload_type == "image":

            return jsonify({
                "success": False,
                "message": "Image hiding is under development."
            }), 501

        elif payload_type == "audio":

            return jsonify({
                "success": False,
                "message": "Audio hiding is under development."
            }), 501

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="encode",
                file_type="image",
                file_name=image.filename,
                status="Success",
                file_size=f"{file_size} MB",
            )

        return send_file(
            output_path, as_attachment=True, download_name="encoded_image.png"
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


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
            return jsonify({"success": False, "message": "Image is required"}), 400

        image_name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(UPLOAD_FOLDER, image_name)

        image.save(image_path)

        file_size = round(os.path.getsize(image_path) / (1024 * 1024), 2)

        payload = decode_payload(
            image_path=image_path,
            password=password
        )

        if payload["type"] == "text":

            secret_message = payload["data"].decode("utf-8")

        else:

            return jsonify({
                "success": False,
                "message": "Unsupported payload type."
            }), 400

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="decode",
                file_type="image",
                file_name=image.filename,
                status="Success",
                file_size=f"{file_size} MB"
            )

        return jsonify({"success": True, "message": secret_message})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
