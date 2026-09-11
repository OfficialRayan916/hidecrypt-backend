from pydub import AudioSegment
import os
import wave
import struct
import base64
import hashlib
from cryptography.fernet import Fernet
from PIL import Image


def convert_to_wav(input_file):

    extension = os.path.splitext(input_file)[1].lower()

    if extension == ".wav":
        return input_file

    wav_file = os.path.splitext(input_file)[0] + ".wav"

    audio = AudioSegment.from_file(input_file)

    audio.export(wav_file, format="wav")

    return wav_file


def compress_audio(input_file):

    compressed_file = os.path.splitext(input_file)[0] + "_compressed.mp3"

    audio = AudioSegment.from_file(input_file)

    audio.export(compressed_file, format="mp3", bitrate="64k")

    return compressed_file


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def create_payload(payload_type, payload_path=None, text=None):

    if payload_type == "text":

        payload_bytes = text.encode("utf-8")
        extension = "txt"

    elif payload_type == "image":

        # Compress secret image before embedding
        temp_image = os.path.splitext(payload_path)[0] + "_compressed.jpg"

        image = Image.open(payload_path)

        # JPEG requires RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Compress image to JPEG quality 70
        image.save(temp_image, format="JPEG", quality=70, optimize=True)

        extension = "jpg"

        # Read compressed image bytes
        with open(temp_image, "rb") as file:
            payload_bytes = file.read()

        # Remove temporary compressed image
        os.remove(temp_image)

    elif payload_type == "audio":

        # Compress secret audio before embedding
        compressed_audio = compress_audio(payload_path)

        extension = "mp3"

        # Read compressed audio bytes
        with open(compressed_audio, "rb") as file:
            payload_bytes = file.read()

        # Remove temporary compressed audio file
        os.remove(compressed_audio)

    else:

        raise Exception("Invalid payload type")

    type_bytes = payload_type.encode()

    extension_bytes = extension.encode()

    payload = (
        struct.pack(">I", len(type_bytes))
        + type_bytes
        + struct.pack(">I", len(extension_bytes))
        + extension_bytes
        + struct.pack(">I", len(payload_bytes))
        + payload_bytes
    )

    return payload


def read_payload(payload):

    index = 0

    # ---------- TYPE ----------

    type_length = struct.unpack(">I", payload[index : index + 4])[0]

    index += 4

    payload_type = payload[index : index + type_length].decode()

    index += type_length

    # ---------- EXTENSION ----------

    extension_length = struct.unpack(">I", payload[index : index + 4])[0]

    index += 4

    extension = payload[index : index + extension_length].decode()

    index += extension_length

    # ---------- DATA ----------

    data_length = struct.unpack(">I", payload[index : index + 4])[0]

    index += 4

    payload_bytes = payload[index : index + data_length]

    return {"type": payload_type, "extension": extension, "data": payload_bytes}


def encode_payload(
    input_audio, payload_type, output_audio, password=None, text=None, payload_path=None
):

    payload = create_payload(
        payload_type=payload_type, payload_path=payload_path, text=text
    )

    if password:

        key = generate_key(password)

        cipher = Fernet(key)

        payload = cipher.encrypt(payload)

    input_audio = convert_to_wav(input_audio)

    audio = wave.open(input_audio, "rb")

    frames = bytearray(audio.readframes(audio.getnframes()))

    params = audio.getparams()

    audio.close()

    payload_length = len(payload)

    length_bytes = struct.pack(">I", payload_length)

    payload = length_bytes + payload

    binary_payload = "".join(format(byte, "08b") for byte in payload)

    if len(binary_payload) > len(frames):
        raise Exception("Payload is too large for this audio file")

    for i in range(len(binary_payload)):

        frames[i] = (frames[i] & 254) | int(binary_payload[i])

    encoded = wave.open(output_audio, "wb")

    encoded.setparams(params)

    encoded.writeframes(bytes(frames))

    encoded.close()


def decode_bytes(input_audio):

    input_audio = convert_to_wav(input_audio)

    audio = wave.open(input_audio, "rb")

    frames = bytearray(list(audio.readframes(audio.getnframes())))

    audio.close()

    binary_data = ""

    for byte in frames:

        binary_data += str(byte & 1)

    payload_bytes = bytearray()

    for i in range(0, len(binary_data), 8):

        byte = binary_data[i : i + 8]

        if len(byte) < 8:
            break

        payload_bytes.append(int(byte, 2))

    payload_length = struct.unpack(">I", payload_bytes[:4])[0]

    return bytes(payload_bytes[4 : 4 + payload_length])


def decode_payload(input_audio, password=None):

    payload = decode_bytes(input_audio)

    if password:

        key = generate_key(password)

        cipher = Fernet(key)

        try:
            payload = cipher.decrypt(payload)
        except:
            raise Exception("Invalid password")

    return read_payload(payload)
