import boto3
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Model ID for prompt optimization (Claude)
CLAUDE_MODEL_ID = "anthropic.claude-v2"

def lambda_handler(event, context):
    # Retrieve the original prompt and user feedback from the event
    prompt = event.get('prompt')
    suggestion = event.get('suggestion')

    if not prompt or not suggestion:
        logger.error("Missing 'prompt' or 'suggestion' in the event data")
        return {
            "statusCode": 400,
            "message": "Missing 'prompt' or 'suggestion' in the request."
        }

    # Format the Claude-compatible prompt with user feedback
    assistant_prompt = f"\n\nHuman: Original prompt was: \"{prompt}\". User provided the following feedback: {suggestion}\n\nAssistant:(IN ENGLISH, ONLY NEW PROMPT, number of words less than 512)"

    # Generate optimized prompt using Claude
    try:
        new_prompt = call_bedrock_claude(assistant_prompt)
        logger.info(f"Optimized prompt: {new_prompt}")
        return {
            "statusCode": 200,
            "optimized_prompt": new_prompt
        }
    except Exception as e:
        logger.error(f"Error optimizing prompt: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Error optimizing prompt: {str(e)}"
        }

def call_bedrock_claude(prompt):
    """
    Calls the Claude model on AWS Bedrock to generate an optimized prompt.
    """
    bedrock = boto3.client('bedrock-runtime')

    # Construct payload for Claude with required parameters
    payload = {
        "prompt": prompt,
        "max_tokens_to_sample": 300,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 250,
        "stop_sequences": ["\n\nHuman:"]
    }

    body = json.dumps(payload)

    # Invoke Claude model
    response = bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=body
    )

    # Parse response
    response_body = json.loads(response['body'].read())
    new_prompt = response_body.get('completion', '').strip()

    return new_prompt
