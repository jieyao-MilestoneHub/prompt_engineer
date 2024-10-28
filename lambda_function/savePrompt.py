import boto3
import hashlib
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize DynamoDB resource and table
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("SavedPrompts")  # Ensure this matches your actual table name

    # Get data from the event
    prompt = event.get("prompt")
    rating = event.get("rating")
    seed = event.get("seed")

    # Validate required fields
    if not prompt or not rating:
        logger.error("Missing 'prompt' or 'rating' in the event data")
        return {
            "statusCode": 400,
            "message": "Missing 'prompt' or 'rating' in the request."
        }

    # Generate a hash of the prompt to use as the primary key
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()

    # Log the prompt and hash for debugging
    logger.info(f"Generated hash for prompt: {prompt_hash}")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Rating: {rating}")
    logger.info(f"Seed: {seed}")

    # Create the item to store in DynamoDB
    item = {
        "uuid": prompt_hash,  # Use the hash as a unique identifier
        "prompt": prompt,
        "seed": seed,
        "rating": str(rating),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Attempt to save the item to DynamoDB
    try:
        response = table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")  # Log DynamoDB response for verification
        return {
            "statusCode": 200,
            "message": "Prompt saved successfully."
        }
    except Exception as e:
        logger.error(f"Error saving prompt to DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Error saving prompt: {str(e)}"
        }
