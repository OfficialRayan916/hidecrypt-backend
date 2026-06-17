from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file
from services.audio_steganography import (
    encode_audio,
    decode_audio
)

import os
import uuid

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

        user_id = request.form.get("user_id")
        username = request.form.get("username")
        password = request.form.get("password")

        if not audio:
            return jsonify({
                "success": False,
                "message": "Audio file is required"
            }), 400

        if not secret_message:
            return jsonify({
                "success": False,
                "message": "Secret message is required"
            }), 400

        extension = os.path.splitext(
            audio.filename
        )[1]

        audio_name = f"{uuid.uuid4()}{extension}"

        input_path = os.path.join(
            UPLOAD_FOLDER,
            audio_name
        )

        output_path = os.path.join(
            ENCODED_FOLDER,
            audio_name
        )

        audio.save(input_path)

        encode_audio(
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
                file_type="audio"
            )

        return send_file(
            output_path,
            as_attachment=True,
            download_name="encoded_audio.wav"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


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
            return jsonify({
                "success": False,
                "message": "Audio file is required"
            }), 400

        extension = os.path.splitext(
            audio.filename
        )[1]

        audio_name = f"{uuid.uuid4()}{extension}"

        audio_path = os.path.join(
            UPLOAD_FOLDER,
            audio_name
        )

        audio.save(audio_path)

        secret_message = decode_audio(
            audio_path,
            password
        )

        if user_id and username:
            create_log(
                user_id=user_id,
                username=username,
                operation="decode",
                file_type="audio"
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