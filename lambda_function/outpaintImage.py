import base64
import json
import logging
import boto3
import io
from PIL import Image
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Custom Exception
class ImageError(Exception):
    """Custom exception for errors returned by Amazon Titan Image Generator G1"""
    def __init__(self, message):
        self.message = message

# Main function to generate an outpainted image
def lambda_handler(event, context):
    """
    Lambda handler to process outpainting request with Amazon Titan Image Generator G1.
    Args:
        event (dict): Contains prompt, seed, image, mask_image, and other outpainting parameters.
    Returns:
        dict: Contains base64 encoded generated image or an error message.
    """
    # Parameters extraction from event
    prompt = event.get('prompt', "Expand the scene")
    model_id = 'amazon.titan-image-generator-v1'
    mask_image_data = event.get('mask_image_data')
    input_image_data = event.get('input_image_data')
    
    # Check for required parameters
    if not input_image_data or not mask_image_data:
        error_msg = "Both input_image_data and mask_image_data are required."
        logger.error(error_msg)
        return {"statusCode": 400, "message": error_msg}

    # Body configuration for Titan outpainting
    body = json.dumps({
        "taskType": "OUTPAINTING",
        "outPaintingParams": {
            "text": prompt,
            "negativeText": "bad quality, low res",
            "image": input_image_data,
            "maskImage": mask_image_data,
            "outPaintingMode": "DEFAULT"
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": event.get("height", 512),
            "width": event.get("width", 512),
            "cfgScale": 8.0
        }
    })

    try:
        # Generate the outpainted image using Titan Image Generator
        image_bytes = generate_image(model_id=model_id, body=body)
        # Encode image as base64 for return
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "statusCode": 200,
            "image_data": image_base64,
            "message": "Image generated successfully."
        }
    except ClientError as err:
        error_msg = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", error_msg)
        return {"statusCode": 500, "message": f"A client error occurred: {error_msg}"}
    except ImageError as err:
        logger.error(err.message)
        return {"statusCode": 500, "message": err.message}

# Helper function to call the Amazon Titan Image Generator
def generate_image(model_id, body):
    """
    Calls the Amazon Titan Image Generator G1 model to generate an image based on the provided body.
    """
    bedrock = boto3.client(service_name='bedrock-runtime')
    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    # Process and check response
    if "error" in response_body:
        raise ImageError(f"Image generation error: {response_body['error']}")
    
    base64_image = response_body["images"][0]
    image_bytes = base64.b64decode(base64_image)
    return image_bytes
