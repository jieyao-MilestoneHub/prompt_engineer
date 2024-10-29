import boto3
import json

# Initialize AWS Lambda and DynamoDB clients
lambda_client = boto3.client('lambda', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Lambda function ARNs
LAMBDA_FUNCTIONS = {
    "outpaint": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11552571976-OutpaintFunction",
    "image_generator": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11552571976-ImageProcessingFunction",
    "optimize_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11552571976-OptimizePromptFunction",
    "save_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11552571976-SavePromptFunction",
    "add_label": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11552571976-AddLabelFunction"
}

def invoke_lambda(function_name, payload):
    """Invoke a specified Lambda function with the given payload."""
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTIONS[function_name],
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )
        return json.loads(response['Payload'].read())
    except Exception as e:
        raise RuntimeError(f"Error calling {function_name} Lambda: {str(e)}")
