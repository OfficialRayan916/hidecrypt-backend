from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file

from services.video_steganography import encode_video, decode_video

import os
import uuid

video_bp = Blueprint("video", __name__)

UPLOAD_FOLDER = "uploads_video"
ENCODED_FOLDER = "encoded_video"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)


# =========================
# ENCODE VIDEO
# =========================
@video_bp.route("/encode", methods=["POST"])
def encode():

    print("✅ VIDEO ENCODE HIT")

    try:

        video = request.files.get("video")
        secret_message = request.form.get("message")

        user_id = request.form.get("user_id")
        username = request.form.get("username")

        password = request.form.get("password")

        if not video:
            return jsonify({"success": False, "message": "Video file is required"}), 400

        if not secret_message:
            return (
                jsonify({"success": False, "message": "Secret message is required"}),
                400,
            )

        extension = os.path.splitext(video.filename)[1]

        filename = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_FOLDER, filename + extension)

        output_path = os.path.join(ENCODED_FOLDER, filename + "_encoded.avi")

        video.save(input_path)

        file_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)

        encode_video(input_path, secret_message, output_path, password)

        if user_id and username:

            create_log(
                user_id=user_id,
                username=username,
                operation="encode",
                file_type="video",
                file_name="video.filename",
                status="Success",
                file_size=f"{file_size} MB",
            )

        original_name = os.path.splitext(video.filename)[0]

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{original_name}_encoded.avi",
        )

    except Exception as e:

        return jsonify({"success": False, "message": str(e)}), 500


# =========================
# DECODE VIDEO
# =========================
@video_bp.route("/decode", methods=["POST"])
def decode():

    print("✅ VIDEO DECODE HIT")

    try:

        video = request.files.get("video")

        password = request.form.get("password")

        user_id = request.form.get("user_id")
        username = request.form.get("username")

        if not video:
            return jsonify({"success": False, "message": "Video file is required"}), 400

        extension = os.path.splitext(video.filename)[1]

        filename = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_FOLDER, filename + extension)

        video.save(input_path)

        file_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)

        secret_message = decode_video(input_path, password)

        if user_id and username:

            create_log(
                user_id=user_id,
                username=username,
                operation="decode",
                file_type="video",
                file_name="video.filename",
                status="Success",
                file_size=f"{file_size} MB",
            )

        return jsonify({"success": True, "message": secret_message})

    except Exception as e:

        return jsonify({"success": False, "message": str(e)}), 500
