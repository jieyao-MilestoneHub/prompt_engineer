import boto3
import hashlib
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize DynamoDB resource and table
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("LabelsTable")  # Make sure this matches your actual table name

    # Get label data from the event
    label_name = event.get("label_name")

    # Validate the required field
    if not label_name:
        logger.error("Missing 'label_name' in the event data")
        return {
            "statusCode": 400,
            "message": "Missing 'label_name' in the request."
        }

    # Generate a unique identifier for the label
    label_id = hashlib.sha256(label_name.encode('utf-8')).hexdigest()

    # Log the label details for debugging
    logger.info(f"Generated label_id: {label_id}")
    logger.info(f"Label name: {label_name}")

    # Create the item to store in DynamoDB
    item = {
        "label_id": label_id,  # Unique identifier for the label
        "label_name": label_name
    }

    # Attempt to save the item to DynamoDB
    try:
        response = table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")  # Log DynamoDB response for verification
        return {
            "statusCode": 200,
            "message": "Label saved successfully."
        }
    except Exception as e:
        logger.error(f"Error saving label to DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Error saving label: {str(e)}"
        }
