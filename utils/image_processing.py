import base64

def encode_image(file):
    """Encode an uploaded image file as base64."""
    return base64.b64encode(file.read()).decode("utf-8")

def decode_image(image_data):
    """Decode base64 image data to bytes."""
    return base64.b64decode(image_data)
