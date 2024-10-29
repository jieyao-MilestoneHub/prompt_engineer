import base64
from io import BytesIO
from PIL import Image

def encode_image_to_base64(image_file):
    """Encode an image file to base64."""
    return base64.b64encode(image_file.read()).decode("utf-8")

def decode_image_from_base64(image_data):
    """Decode a base64 image to PIL format."""
    image_bytes = base64.b64decode(image_data)
    return Image.open(BytesIO(image_bytes))
