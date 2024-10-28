import boto3
import hashlib
import logging
import json

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize DynamoDB resource and table
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("LabelsTable")  # Ensure this matches your actual table name

    # Get label data from the event
    label_name = event.get("label_name")

    # Validate the required field
    if not label_name:
        logger.error("Missing 'label_name' in the event data")
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing 'label_name' in the request."})
        }

    # Generate a unique identifier for the label
    label_id = hashlib.sha256(label_name.encode('utf-8')).hexdigest()

    # Check if label already exists in DynamoDB
    try:
        response = table.get_item(Key={"label_id": label_id})
        if "Item" in response:
            return {
                "statusCode": 409,  # Conflict status code
                "body": json.dumps({
                    "label_id": label_id,
                    "label_name": label_name,
                    "message": "Label already exists."
                })
            }
    except Exception as e:
        logger.error(f"Error checking for existing label: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error checking for label: {str(e)}"})
        }

    # Create the item to store in DynamoDB
    item = {
        "label_id": label_id,
        "label_name": label_name
    }

    # Attempt to save the item to DynamoDB
    try:
        response = table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "label_id": label_id,
                "label_name": label_name,
                "message": "Label saved successfully."
            })
        }
    except Exception as e:
        logger.error(f"Error saving label to DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error saving label: {str(e)}"})
        }
