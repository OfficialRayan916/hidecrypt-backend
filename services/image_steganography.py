import base64
import hashlib
import os
import struct
from cryptography.fernet import Fernet
from PIL import Image
from pydub import AudioSegment


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def compress_audio(input_file):
    compressed_file = os.path.splitext(input_file)[0] + "_compressed.mp3"

    audio = AudioSegment.from_file(input_file)

    audio.export(compressed_file, format="mp3", bitrate="64k")

    return compressed_file


def compress_image(input_file):
    compressed_file = os.path.splitext(input_file)[0] + "_compressed.jpg"

    image = Image.open(input_file)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(compressed_file, "JPEG", quality=70, optimize=True)

    return compressed_file


def create_payload(payload_type, payload_path=None, text=None):
    """
    Payload Format

    -----------------------------------

    TYPE_LENGTH (4 bytes)

    TYPE

    EXT_LENGTH (4 bytes)

    EXTENSION

    DATA_LENGTH (4 bytes)

    DATA

    -----------------------------------
    """

    if payload_type == "text":

        payload_bytes = text.encode("utf-8")

        extension = "txt"

    elif payload_type == "image":
        # Compress secret image before embedding
        compressed_image = compress_image(payload_path)

        # Embedded image will be JPEG
        extension = "jpg"

        # Read compressed image bytes
        with open(compressed_image, "rb") as file:
            payload_bytes = file.read()

        # Remove temporary compressed image
        os.remove(compressed_image)

    elif payload_type == "audio":

        # Compress secret audio before embedding
        compressed_audio = compress_audio(payload_path)

        # Embedded audio will be MP3
        extension = "mp3"

        # Read compressed audio bytes
        with open(compressed_audio, "rb") as file:

            payload_bytes = file.read()

        # Remove temporary compressed file
        os.remove(compressed_audio)

    else:

        raise Exception("Invalid payload type")

    type_bytes = payload_type.encode()

    ext_bytes = extension.encode()

    payload = (
        struct.pack(">I", len(type_bytes))
        + type_bytes
        + struct.pack(">I", len(ext_bytes))
        + ext_bytes
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


def encode_bytes(image_path, payload_bytes, output_path):

    image = Image.open(image_path)
    image = image.convert("RGB")

    pixels = image.load()

    width, height = image.size

    # Store payload length in the first 4 bytes
    length_header = struct.pack(">I", len(payload_bytes))

    # Combine length header + actual payload
    complete_payload = length_header + payload_bytes

    # Convert payload to binary
    binary_payload = "".join(format(byte, "08b") for byte in complete_payload)

    # Calculate image capacity
    capacity = (width * height * 3) // 8

    print("Image Capacity:", capacity, "bytes")
    print("Payload Size:", len(payload_bytes), "bytes")
    print("Required Size:", len(complete_payload), "bytes")

    # Check capacity before encoding
    if len(complete_payload) > capacity:
        raise Exception(
            f"Payload is too large for this image. "
            f"Required: {len(complete_payload)} bytes, "
            f"Available: {capacity} bytes"
        )

    data_index = 0

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            if data_index < len(binary_payload):
                r = (r & ~1) | int(binary_payload[data_index])
                data_index += 1

            if data_index < len(binary_payload):
                g = (g & ~1) | int(binary_payload[data_index])
                data_index += 1

            if data_index < len(binary_payload):
                b = (b & ~1) | int(binary_payload[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b)

            if data_index >= len(binary_payload):

                image.save(output_path)

                return output_path

    raise Exception("Payload is too large for this image")


def decode_bytes(image_path):

    image = Image.open(image_path)
    image = image.convert("RGB")

    pixels = image.load()

    width, height = image.size

    # First extract 32 bits = 4 bytes for payload length
    header_bits = ""

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            header_bits += str(r & 1)

            if len(header_bits) >= 32:
                break

            header_bits += str(g & 1)

            if len(header_bits) >= 32:
                break

            header_bits += str(b & 1)

            if len(header_bits) >= 32:
                break

        if len(header_bits) >= 32:
            break

    # Make sure header exists
    if len(header_bits) < 32:
        raise Exception("No hidden payload found")

    # Convert first 32 bits to payload length
    payload_length = int(header_bits, 2)

    capacity = (width * height * 3) // 8

    # Validate payload length
    if payload_length <= 0:
        raise Exception("Invalid hidden payload")

    if payload_length > capacity - 4:
        raise Exception("Invalid or corrupted hidden payload")

    # Now extract the complete payload
    required_bits = (payload_length + 4) * 8

    binary_data = ""

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            binary_data += str(r & 1)

            if len(binary_data) >= required_bits:
                break

            binary_data += str(g & 1)

            if len(binary_data) >= required_bits:
                break

            binary_data += str(b & 1)

            if len(binary_data) >= required_bits:
                break

        if len(binary_data) >= required_bits:
            break

    # Remove the first 32 bits containing the payload length
    payload_binary = binary_data[32:required_bits]

    payload_bytes = bytearray()

    for i in range(0, len(payload_binary), 8):

        byte = payload_binary[i : i + 8]

        if len(byte) < 8:
            raise Exception("Incomplete hidden payload")

        payload_bytes.append(int(byte, 2))

    return bytes(payload_bytes)


def encode_payload(
    image_path, payload_type, output_path, password=None, text=None, payload_path=None
):

    # Create universal payload
    payload = create_payload(
        payload_type=payload_type, payload_path=payload_path, text=text
    )

    # Encrypt payload if password is provided
    if password:

        key = generate_key(password)

        cipher = Fernet(key)

        payload = cipher.encrypt(payload)

    # Hide payload inside cover image
    print("Payload Size:", len(payload), "bytes")
    encode_bytes(image_path=image_path, payload_bytes=payload, output_path=output_path)

    return output_path


def decode_payload(image_path, password=None):

    # Extract raw payload bytes
    payload = decode_bytes(image_path)

    # Decrypt if password was used
    if password:

        try:

            key = generate_key(password)

            cipher = Fernet(key)

            payload = cipher.decrypt(payload)

        except Exception:

            raise Exception("Wrong password")

    # Convert payload bytes back into data
    payload_info = read_payload(payload)

    return payload_info


#                  temporary delete it remember


def encode_message(image_path, secret_message, output_path, password=None):
    return encode_payload(
        image_path=image_path,
        payload_type="text",
        output_path=output_path,
        password=password,
        text=secret_message,
    )


def decode_message(image_path, password=None):
    payload = decode_payload(image_path=image_path, password=password)

    if payload["type"] != "text":
        raise Exception("Hidden payload is not text")

    return payload["data"].decode("utf-8")
