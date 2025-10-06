import io
from rembg import remove

def remove_background(image_bytes: bytes) -> bytes:
    return remove(image_bytes)
