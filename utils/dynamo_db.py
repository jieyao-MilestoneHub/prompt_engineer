import boto3
import streamlit as st
from config import AWS_REGION, LABELS_TABLE_NAME

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
labels_table = dynamodb.Table(LABELS_TABLE_NAME)

def get_labels():
    """Retrieve existing labels from DynamoDB."""
    try:
        response = labels_table.scan(ConsistentRead=False)
        return {item['label_id']: item['label_name'] for item in response.get('Items', [])}
    except Exception as e:
        st.error(f"Error retrieving labels: {str(e)}")
        return {}
