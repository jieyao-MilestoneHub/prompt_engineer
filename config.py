# config.py
import os

# AWS Configuration
AWS_REGION = 'us-east-1'

# Lambda Function ARNs (replace placeholders with your actual ARNs or use environment variables)
LAMBDA_ARNS = {
    "outpaint": os.environ.get('OUTPAINT_LAMBDA_ARN', 'arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569818451-OutpaintFunction'),
    "optimize_prompt": os.environ.get('OPTIMIZE_PROMPT_LAMBDA_ARN', 'arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569818451-OptimizePromptFunction'),
    "save_prompt": os.environ.get('SAVE_PROMPT_LAMBDA_ARN', 'arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569818451-SavePromptFunction'),
    "add_label": os.environ.get('ADD_LABEL_LAMBDA_ARN', 'arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569818451-AddLabelFunction'),
}

# DynamoDB Table Names
LABELS_TABLE_NAME = os.environ.get('LABELS_TABLE_NAME', 'LabelsTable')
