import os
import cv2
import tempfile
from moviepy import VideoFileClip

from services.image_steganography import encode_message, decode_message

from services.audio_steganography import (
    create_payload,
    read_payload,
    generate_key
)

from cryptography.fernet import Fernet


# =========================
# CONVERT TO MP4
# =========================
def convert_to_mp4(input_file):

    extension = os.path.splitext(input_file)[1].lower()

    if extension == ".mp4":
        return input_file

    output_file = os.path.splitext(input_file)[0] + "_converted.mp4"

    clip = VideoFileClip(input_file)

    clip.write_videofile(output_file, codec="libx264", audio_codec="aac", logger=None)

    clip.close()

    return output_file


# =========================
# ENCODE VIDEO
# =========================
def encode_video(
    input_video,
    payload_type,
    output_video,
    password=None,
    text=None,
    payload_path=None
):

    print("ENCODE 1")

    payload = create_payload(
       payload_type=payload_type,
       payload_path=payload_path,
       text=text
    )

    if password:

        key = generate_key(password)

        cipher = Fernet(key)

        payload = cipher.encrypt(payload)
 
    input_video = convert_to_mp4(input_video)

    temp_dir = tempfile.mkdtemp()

    frame_path = os.path.join(temp_dir, "frame.png")

    encoded_frame_path = os.path.join(temp_dir, "encoded_frame.png")

    print("ENCODE 2")
    cap = cv2.VideoCapture(input_video)

    print("ENCODE 3")
    success, frame = cap.read()
    print("ENCODE 4")

    if not success:
        cap.release()
        raise Exception("Unable to read video")

    cv2.imwrite(frame_path, frame)

    encode_message(
    frame_path,
    payload.hex(),
    encoded_frame_path,
    None
)

    encoded_frame = cv2.imread(encoded_frame_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_video = os.path.join(temp_dir, "video_no_audio.avi")

    writer = cv2.VideoWriter(
        temp_video, cv2.VideoWriter_fourcc(*"FFV1"), fps, (width, height)
    )

    writer.write(encoded_frame)

    while True:

        success, frame = cap.read()

        if not success:
            break

        writer.write(frame)

    cap.release()
    writer.release()

    original_clip = VideoFileClip(input_video)

    encoded_clip = VideoFileClip(temp_video)

    final_clip = encoded_clip.with_audio(original_clip.audio)

    final_clip.write_videofile(
        output_video, codec="ffv1", audio_codec="pcm_s16le", logger=None
    )

    original_clip.close()
    encoded_clip.close()
    final_clip.close()

    return output_video


# =========================
# DECODE VIDEO
# =========================
def decode_video(input_video, password=None):
    print("test 1")
    # input_video = convert_to_mp4(
    #     input_video
    # )

    print("test 2")
    temp_dir = tempfile.mkdtemp()

    frame_path = os.path.join(temp_dir, "decode_frame.png")

    cap = cv2.VideoCapture(input_video)

    print("test 3")
    success, frame = cap.read()

    print("test 4")
    cap.release()

    if not success:
        raise Exception("Unable to read video")

    cv2.imwrite(frame_path, frame)

    payload_hex = decode_message(
        frame_path,
        None
    )

    payload = bytes.fromhex(payload_hex)

    if password:

        key = generate_key(password)

        cipher = Fernet(key)

        payload = cipher.decrypt(payload)

    return read_payload(payload)
