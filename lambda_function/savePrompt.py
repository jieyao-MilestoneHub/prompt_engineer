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
    table = dynamodb.Table("PromptsTable")  # Ensure this matches your table name in the template

    # Get data from the event
    prompt = event.get("prompt")
    rating = event.get("rating")
    seed = event.get("seed")
    labels = event.get("labels", [])  # Get labels, default to an empty list if not provided

    # Validate required fields
    if not prompt or not rating:
        logger.error("Missing 'prompt' or 'rating' in the event data")
        return {
            "statusCode": 400,
            "message": "Missing 'prompt' or 'rating' in the request."
        }

    # Generate a hash of the prompt to use as the primary key
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    labels_string = ", ".join(labels)

    # Log the prompt and hash for debugging
    logger.info(f"Generated hash for prompt: {prompt_hash}")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Rating: {rating}")
    logger.info(f"Seed: {seed}")
    logger.info(f"Labels: {labels_string}")

    # Create the item to store in DynamoDB
    item = {
        "prompt_id": prompt_hash,  # Use prompt_id to match the table's primary key definition
        "prompt": prompt,
        "seed": seed,
        "rating": str(rating),
        "labels": labels_string or "N/A",  # Add labels here
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
