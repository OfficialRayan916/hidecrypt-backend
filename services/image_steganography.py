import base64
import hashlib
import os
import struct
from cryptography.fernet import Fernet
from PIL import Image
from PIL import Image


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


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

        extension = os.path.splitext(payload_path)[1][1:]

        with open(payload_path, "rb") as file:

            payload_bytes = file.read()

    elif payload_type == "audio":

        extension = os.path.splitext(payload_path)[1][1:]

        with open(payload_path, "rb") as file:

            payload_bytes = file.read()

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

    binary_payload = "".join(format(byte, "08b") for byte in payload_bytes)

    # END MARKER
    binary_payload += "1111111111111110"

    pixels = image.load()

    width, height = image.size
    capacity = (width * height * 3) // 8

    print("Image Capacity:", capacity, "bytes")

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

    binary_data = ""

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    end_marker = "1111111111111110"

    marker_index = binary_data.find(end_marker)

    if marker_index == -1:

        raise Exception("No hidden payload found")

    binary_data = binary_data[:marker_index]

    payload_bytes = bytearray()

    for i in range(0, len(binary_data), 8):

        byte = binary_data[i : i + 8]

        if len(byte) < 8:
            break

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


def encode_message(
    image_path,
    secret_message,
    output_path,
    password=None
):
    return encode_payload(
        image_path=image_path,
        payload_type="text",
        output_path=output_path,
        password=password,
        text=secret_message
    )


def decode_message(
    image_path,
    password=None
):
    payload = decode_payload(
        image_path=image_path,
        password=password
    )

    if payload["type"] != "text":
        raise Exception("Hidden payload is not text")

    return payload["data"].decode("utf-8")