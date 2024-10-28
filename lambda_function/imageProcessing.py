import boto3
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Model ID for image generation
IMAGE_MODEL_ID = "stability.stable-diffusion-xl-v1"

def lambda_handler(event, context):
    # Retrieve prompt, seed, and style from event
    prompt = event.get('prompt')
    seed = event.get('seed', 42)
    style = event.get('style', 'photographic')

    if not prompt:
        logger.error("Missing 'prompt' in the event data")
        return {
            "statusCode": 400,
            "message": "Missing 'prompt' in the request."
        }

    # Generate image using the prompt
    try:
        image_data = generate_image(prompt, seed, style)
        return {
            "statusCode": 200,
            "image_data": image_data,
            "seed": seed,
            "style": style
        }
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Error generating image: {str(e)}"
        }

def generate_image(prompt, seed, style):
    """
    Calls the image generation model and returns base64 encoded image data.
    """
    payload = {
        "text_prompts": [{"text": prompt}],
        "style_preset": style,
        "seed": seed,
        "cfg_scale": 10,
        "steps": 30
    }

    body = json.dumps(payload)

    # Call image generation model
    bedrock = boto3.client("bedrock-runtime")
    response = bedrock.invoke_model(
        modelId=IMAGE_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=body
    )

    # Parse response
    response_body = json.loads(response['body'].read())
    artifact = response_body.get("artifacts")[0]
    base64_image = artifact.get("base64")

    return base64_image
