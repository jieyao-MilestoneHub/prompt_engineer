import boto3
import json
import streamlit as st
from config import AWS_REGION, LAMBDA_ARNS

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

def invoke_lambda(function_name, payload):
    """Invoke a specified Lambda function with the provided payload."""
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_ARNS[function_name],
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )
        result = json.loads(response["Payload"].read())
        if 'FunctionError' in response:
            st.error(f"Error calling {function_name} Lambda function: {result.get('errorMessage', 'Unknown error')}")
            return None
        return result
    except Exception as e:
        st.error(f"Error calling {function_name} Lambda function: {str(e)}")
        return None
