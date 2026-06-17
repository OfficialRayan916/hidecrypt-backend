from services.audio_steganography import (
    encode_audio,
    decode_audio
)

encode_audio(
    "sample.wav",
    "Hello Rayan",
    "encoded.wav",
    "123"
)

message = decode_audio(
    "encoded.wav",
    "123"
)

print(message)