import base64
import hashlib
from cryptography.fernet import Fernet
from PIL import Image


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()


def decrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(message.encode()).decode()


def encode_message(
    image_path,
    secret_message,
    output_path,
    password=None
):

    image = Image.open(image_path)
    image = image.convert("RGB")

    if password:
        secret_message = encrypt_message(
            secret_message,
            password
        )

    binary_message = ''.join(
        format(ord(char), '08b')
        for char in secret_message
    )

    binary_message += "1111111111111110"

    pixels = image.load()

    width, height = image.size

    data_index = 0

    for y in range(height):
        for x in range(width):

            r, g, b = pixels[x, y]

            if data_index < len(binary_message):
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1

            if data_index < len(binary_message):
                g = (g & ~1) | int(binary_message[data_index])
                data_index += 1

            if data_index < len(binary_message):
                b = (b & ~1) | int(binary_message[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b)

            if data_index >= len(binary_message):
                image.save(output_path)
                return output_path

    raise Exception("Message is too large for this image")


def decode_message(
    image_path,
    password=None
):

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
        return "No hidden message found"

    binary_data = binary_data[:marker_index]

    message = ""

    for i in range(0, len(binary_data), 8):

        byte = binary_data[i:i + 8]

        if len(byte) < 8:
            break

        message += chr(int(byte, 2))

    if password:

         try:
             return decrypt_message(
               message,
               password
             )


         except:
             return "Wrong password"


    return message
