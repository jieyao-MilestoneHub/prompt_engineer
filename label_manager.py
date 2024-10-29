from aws_client import dynamodb, invoke_lambda
import streamlit as st

# DynamoDB table
labels_table = dynamodb.Table('LabelsTable')

def get_labels():
    """Retrieve existing labels from DynamoDB."""
    try:
        response = labels_table.scan(ConsistentRead=False)
        return {item['label_id']: item['label_name'] for item in response['Items']}
    except Exception as e:
        st.error(f"Error retrieving labels: {str(e)}")
        return {}

def add_label(label_name):
    """Add a new label using the add_label Lambda function."""
    payload = {'label_name': label_name}
    return invoke_lambda("add_label", payload)
