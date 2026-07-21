from services.log_service import create_log
from flask import Blueprint, request, jsonify, send_file

from services.video_steganography import (
    encode_video,
    decode_video
)

import os
import uuid
import base64

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
        payload_type = request.form.get("payload_type")

        secret_image = request.files.get("secret_image")
        secret_audio = request.files.get("secret_audio")

        user_id = request.form.get("user_id")
        username = request.form.get("username")

        password = request.form.get("password")

        if not video:
            return jsonify({"success": False, "message": "Video file is required"}), 400

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

        extension = os.path.splitext(video.filename)[1]

        filename = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_FOLDER, filename + extension)

        output_path = os.path.join(ENCODED_FOLDER, filename + "_encoded.avi")
 
        video.save(input_path)

        payload_path = None

        if payload_type == "image":

             image_name = f"{uuid.uuid4()}_{secret_image.filename}"

             payload_path = os.path.join(
                 UPLOAD_FOLDER,
                 image_name
             )

             secret_image.save(payload_path)

        elif payload_type == "audio":

            audio_name = f"{uuid.uuid4()}_{secret_audio.filename}"

            payload_path = os.path.join(
                  UPLOAD_FOLDER,
                  audio_name
            )

            secret_audio.save(payload_path)

        file_size = round(os.path.getsize(input_path) / (1024 * 1024), 2)

        encode_video(
           input_video=input_path,
           payload_type=payload_type,
           output_video=output_path,
           password=password,
           text=secret_message,
           payload_path=payload_path,
        )

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

        payload = decode_video(
           input_path,
           password
        )

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

        if payload["type"] == "text":

            response = {
                "success": True,
                "type": "text",
                "message": payload["data"].decode("utf-8"),
            }

        elif payload["type"] == "image":

            image_base64 = base64.b64encode(
                payload["data"]
            ).decode()

            response = {
                "success": True,
                "type": "image",
                "extension": payload["extension"],
                "image": image_base64,
            }

        elif payload["type"] == "audio":

            audio_base64 = base64.b64encode(
                payload["data"]
            ).decode()

            response = {
                "success": True,
                "type": "audio",
                "extension": payload["extension"],
                "audio": audio_base64,
            }

        else:

            return jsonify({
                "success": False,
                "message": "Unsupported payload type"
            }), 400
   
        return jsonify(response)

    except Exception as e:

        return jsonify({"success": False, "message": str(e)}), 500
