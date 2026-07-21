from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file
from services.audio_steganography import encode_payload, decode_payload

import os
import uuid
import base64

audio_bp = Blueprint("audio", __name__)

UPLOAD_FOLDER = "uploads_audio"
ENCODED_FOLDER = "encoded_audio"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)


# =========================
# ENCODE AUDIO
# =========================
@audio_bp.route("/encode", methods=["POST"])
def encode():
    print("✅ AUDIO ENCODE HIT")

    try:

        audio = request.files.get("audio")
        secret_message = request.form.get("message")
        payload_type = request.form.get("payload_type")

        secret_image = request.files.get("secret_image")
        secret_audio = request.files.get("secret_audio")

        user_id = request.form.get("user_id")
        username = request.form.get("username")
        password = request.form.get("password")

        if not audio:
            return jsonify({"success": False, "message": "Audio file is required"}), 400

        if payload_type == "text" and not secret_message:
            return (
                jsonify({"success": False, "message": "Secret message is required"}),
                400,
            )

        if payload_type == "image" and not secret_image:
            return (
                jsonify({"success": False, "message": "Secret image is required"}),
                400,
            )

        if payload_type == "audio" and not secret_audio:
            return (
                jsonify({"success": False, "message": "Secret audio is required"}),
                400,
            )

        extension = os.path.splitext(audio.filename)[1]

        audio_name = f"{uuid.uuid4()}{extension}"

        input_path = os.path.join(UPLOAD_FOLDER, audio_name)

        output_path = os.path.join(ENCODED_FOLDER, audio_name)

        audio.save(input_path)
        payload_path = None

        if payload_type == "image":

            image_name = f"{uuid.uuid4()}_{secret_image.filename}"

            payload_path = os.path.join(UPLOAD_FOLDER, image_name)

            secret_image.save(payload_path)

        elif payload_type == "audio":

            secret_name = f"{uuid.uuid4()}_{secret_audio.filename}"

            payload_path = os.path.join(UPLOAD_FOLDER, secret_name)

            secret_audio.save(payload_path)

        file_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)

        encode_payload(
            input_audio=input_path,
            payload_type=payload_type,
            output_audio=output_path,
            password=password,
            text=secret_message,
            payload_path=payload_path,
        )

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="encode",
                file_type="audio",
                file_name=audio.filename,
                status="Success",
                file_size=f"{file_size} MB",
            )

        return send_file(
            output_path, as_attachment=True, download_name="encoded_audio.wav"
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =========================
# DECODE AUDIO
# =========================
@audio_bp.route("/decode", methods=["POST"])
def decode():
    print("✅ AUDIO DECODE HIT")

    try:

        audio = request.files.get("audio")

        password = request.form.get("password")
        user_id = request.form.get("user_id")
        username = request.form.get("username")

        if not audio:
            return jsonify({"success": False, "message": "Audio file is required"}), 400

        extension = os.path.splitext(audio.filename)[1]

        audio_name = f"{uuid.uuid4()}{extension}"

        audio_path = os.path.join(UPLOAD_FOLDER, audio_name)

        audio.save(audio_path)

        file_size = round(os.path.getsize(audio_path) / (1024 * 1024), 2)

        payload = decode_payload(input_audio=audio_path, password=password)

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="decode",
                file_type="audio",
                file_name=audio.filename,
                status="Success",
                file_size=f"{file_size} MB",
            )

        if payload["type"] == "text":

            response = {
                "success": True,
                "type": "text",
                "message": payload["data"].decode("utf-8"),
            }

        elif payload["type"] == "image":

            image_base64 = base64.b64encode(payload["data"]).decode()

            response = {
                "success": True,
                "type": "image",
                "extension": payload["extension"],
                "image": image_base64,
            }

        elif payload["type"] == "audio":

            audio_base64 = base64.b64encode(payload["data"]).decode()

            response = {
                "success": True,
                "type": "audio",
                "extension": payload["extension"],
                "audio": audio_base64,
            }

        else:

            return (
                jsonify({"success": False, "message": "Unsupported payload type"}),
                400,
            )

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
