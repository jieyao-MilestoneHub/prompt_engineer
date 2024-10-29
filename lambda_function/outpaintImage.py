import base64
import json
import logging
import boto3
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
        event (dict): Contains prompt, seed, image, mask_image, or mask_prompt and other outpainting parameters.
    Returns:
        dict: Contains base64 encoded generated image or an error message.
    """
    # Extract parameters from the event
    prompt = event.get('prompt', "Expand the scene")
    model_id = 'amazon.titan-image-generator-v1'
    input_image_data = event.get('input_image_data')
    mask_image_data = event.get('mask_image_data')
    mask_prompt = event.get('mask_prompt')
    seed = event.get('seed')
    height = event.get("height", 512)
    width = event.get("width", 512)

    # Check that input_image_data is provided and either mask_image_data or mask_prompt
    if not input_image_data or not (mask_image_data or mask_prompt):
        error_msg = "input_image_data and either mask_image_data or mask_prompt are required."
        logger.error(error_msg)
        return {"statusCode": 400, "message": error_msg}

    # Prepare the outPaintingParams based on the selected mask option
    outpainting_params = {
        "text": prompt,
        "image": input_image_data,
        "outPaintingMode": "DEFAULT"  # Allow user to select mode if desired
    }

    # Include only the chosen mask option
    if mask_image_data:
        outpainting_params["maskImage"] = mask_image_data
    elif mask_prompt:
        outpainting_params["maskPrompt"] = mask_prompt

    # Body configuration for Titan outpainting
    body = json.dumps({
        "taskType": "OUTPAINTING",
        "outPaintingParams": outpainting_params,
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": height,
            "width": width,
            "cfgScale": 8.0,
            "seed": seed
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
        logger.error("Image generation error: %s", err.message)
        return {"statusCode": 500, "message": err.message}
    except Exception as err:
        logger.error("Unexpected error: %s", str(err))
        return {"statusCode": 500, "message": "An unexpected error occurred."}

# Helper function to call the Amazon Titan Image Generator
def generate_image(model_id, body):
    """
    Calls the Amazon Titan Image Generator G1 model to generate an image based on the provided body.
    """
    bedrock = boto3.client(service_name='bedrock-runtime')
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())

        # Check for errors in the response
        if "error" in response_body:
            raise ImageError(f"Image generation error: {response_body['error']}")

        # Extract the image data
        base64_image = response_body["images"][0]
        image_bytes = base64.b64decode(base64_image)
        return image_bytes

    except KeyError:
        raise ImageError("Malformed response: 'images' field not found in response.")
    except json.JSONDecodeError:
        raise ImageError("Failed to decode JSON response from Titan Image Generator.")
