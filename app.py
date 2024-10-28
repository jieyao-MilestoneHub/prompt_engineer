import streamlit as st
import boto3
import json
import base64
from io import BytesIO
from PIL import Image

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')
st.title("Prompt Engineer")

# User input for prompt and seed
prompt = st.text_input("Enter initial prompt", "A futuristic city at sunset...")
seed = st.number_input("Enter seed value (optional):", value=42, min_value=0)

# Initialize session state
if 'image_generated' not in st.session_state:
    st.session_state.image_generated = False
    st.session_state.image_data = None
    st.session_state.prompt = prompt  # Save initial prompt
    st.session_state.optimized_prompt = None
    st.session_state.rating = 5  # Initialize rating
    st.session_state.prev_prompt = prompt
    st.session_state.prev_seed = seed
    st.session_state.rating_changed = False

# Track prompt and seed changes
prompt_changed = st.session_state.prev_prompt != prompt
seed_changed = st.session_state.prev_seed != seed

# Lambda function ARNs
lambda_function_image_generator = "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-202410281317-ImageProcessingFunction"
lambda_function_optimize_prompt = "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-202410281317-OptimizePromptFunction"
lambda_function_save_prompts = "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-202410281317-SavePromptFunction"

# Generate Image button action
with st.form("generate_image_form"):
    st.subheader("Generate Image")
    generate_image = st.form_submit_button("Generate Image", disabled=not (prompt_changed or seed_changed))
    
    if generate_image:
        payload = {
            "prompt": prompt,
            "seed": seed,
            "style": "photographic"
        }
        try:
            response = lambda_client.invoke(
                FunctionName=lambda_function_image_generator,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload)
            )
            result = json.loads(response['Payload'].read())
            if result.get('statusCode') == 200:
                st.success("Image generated successfully!")
                image_data = result.get('image_data')
                if image_data:
                    # Save image data and prompt to session state
                    st.session_state.image_data = image_data
                    st.session_state.image_generated = True
                    st.session_state.prompt = prompt
                    st.session_state.optimized_prompt = None  # Reset optimized prompt
                    st.session_state.prev_prompt = prompt
                    st.session_state.prev_seed = seed
            else:
                error_message = result.get('message', 'Unknown error')
                st.error(f"Image generation failed: {error_message}")
        except Exception as e:
            st.error(f"Error calling Lambda function: {str(e)}")

# Display generated image and rating slider
if st.session_state.image_generated and st.session_state.image_data:
    image_bytes = base64.b64decode(st.session_state.image_data)
    image = Image.open(BytesIO(image_bytes))
    st.image(image)
    
    # Display rating slider and track if the rating has changed
    st.session_state.rating = st.slider("Rate the generated image (1-10):", 1, 10, st.session_state.rating, on_change=lambda: setattr(st.session_state, 'rating_changed', True))
    
    # Feedback form for prompt optimization
    st.subheader("Provide Feedback to Optimize Prompt")

    # Structured feedback questions
    feedback_composition = st.text_area("Describe improvements in composition (e.g., layout, balance):")
    feedback_lighting = st.text_area("Describe improvements in lighting (e.g., brightness, shadows):")
    feedback_style = st.text_area("Describe preferred style adjustments (e.g., realism, abstract):")
    feedback_details = st.text_area("Describe key features the image should have:")
    feedback_adjustments = st.text_area("Any other specific adjustments:")

    # Optimize Prompt button action
    with st.form("optimize_prompt_form"):
        optimize_prompt = st.form_submit_button("Optimize Prompt and View Result", disabled=not (feedback_composition and feedback_lighting and feedback_style and feedback_details and feedback_adjustments))
        
        if optimize_prompt:
            feedback_payload = {
                "prompt": st.session_state.prompt,
                "seed": seed,
                "style": "photographic",
                "suggestion": (
                    f"Composition: {feedback_composition}\n"
                    f"Lighting: {feedback_lighting}\n"
                    f"Style: {feedback_style}\n"
                    f"Details: {feedback_details}\n"
                    f"Adjustments: {feedback_adjustments}"
                )
            }
            try:
                response = lambda_client.invoke(
                    FunctionName=lambda_function_optimize_prompt,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(feedback_payload)
                )
                result = json.loads(response['Payload'].read())
                if result.get('statusCode') == 200:
                    st.success("New prompt generated based on your feedback!")
                    st.session_state.optimized_prompt = result.get('optimized_prompt')
                    st.subheader("Optimized Prompt")
                    st.write(st.session_state.optimized_prompt)
                else:
                    error_message = result.get('message', 'Unknown error')
                    st.error(f"Error processing feedback: {error_message}")
            except Exception as e:
                st.error(f"Error calling Lambda function: {str(e)}")

# Save Prompt button action
with st.form("save_prompt_form"):
    prompt_to_save = st.session_state.optimized_prompt or st.session_state.prompt
    save_prompt = st.form_submit_button("Save Prompt", disabled=not st.session_state.rating_changed)
    
    if save_prompt:
        save_payload = {
            "prompt": prompt_to_save,
            "rating": st.session_state.rating,
            "seed": seed
        }
        try:
            response = lambda_client.invoke(
                FunctionName=lambda_function_save_prompts,
                InvocationType="RequestResponse",
                Payload=json.dumps(save_payload)
            )
            result = json.loads(response['Payload'].read())
            if result.get('statusCode') == 200:
                st.success("Prompt saved successfully!")
            else:
                error_message = result.get('message', 'Unknown error')
                st.error(f"Error saving prompt: {error_message}")
        except Exception as e:
            st.error(f"Error calling Lambda function: {str(e)}")
