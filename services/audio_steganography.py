from pydub import AudioSegment
import os
import wave
import base64
import hashlib
from cryptography.fernet import Fernet


def convert_to_wav(input_file):

    extension = os.path.splitext(
        input_file
    )[1].lower()

    if extension == ".wav":
        return input_file

    wav_file = os.path.splitext(
        input_file
    )[0] + ".wav"

    audio = AudioSegment.from_file(
        input_file
    )

    audio.export(
        wav_file,
        format="wav"
    )

    return wav_file


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


def encode_audio(input_audio, secret_message, output_audio, password=None):

    if password:
        secret_message = encrypt_message(
            secret_message,
            password
        )

    secret_message += "#####"

    input_audio = convert_to_wav(
        input_audio
    )

    audio = wave.open(
        input_audio,
        "rb"
    )

    frames = bytearray(
        list(audio.readframes(audio.getnframes()))
    )

    audio.close()

    binary_message = ''.join(
        format(ord(char), '08b')
        for char in secret_message
    )

    if len(binary_message) > len(frames):
        raise Exception(
            "Message is too large for this audio file"
        )

    for i in range(len(binary_message)):
        frames[i] = (
            frames[i] & 254
        ) | int(binary_message[i])

    encoded_audio = wave.open(
        output_audio,
        "wb"
    )

    original = wave.open(
        input_audio,
        "rb"
    )

    encoded_audio.setparams(
        original.getparams()
    )

    encoded_audio.writeframes(
        bytes(frames)
    )

    encoded_audio.close()
    original.close()


def decode_audio(input_audio, password=None):

    input_audio = convert_to_wav(
        input_audio
    )

    audio = wave.open(
        input_audio,
        "rb"
    )

    frames = bytearray(
        list(audio.readframes(audio.getnframes()))
    )

    audio.close()

    extracted_bits = ""

    for byte in frames:
        extracted_bits += str(byte & 1)

    message = ""

    for i in range(
        0,
        len(extracted_bits),
        8
    ):
        byte = extracted_bits[i:i + 8]

        if len(byte) < 8:
            break

        message += chr(int(byte, 2))

        if message.endswith("#####"):
            message = message[:-5]
            break

    if password:
        try:
            message = decrypt_message(
                message,
                password
            )
        except:
            raise Exception(
                "Invalid password"
            )

    return message
