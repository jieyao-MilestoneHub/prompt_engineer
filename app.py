import streamlit as st
import boto3
import json
import base64
from io import BytesIO
from PIL import Image

# --- AWS Lambda Configuration ---
LAMBDA_ARNS = {
    "outpaint": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11568890345-OutpaintFunction",
    "optimize_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11568890345-OptimizePromptFunction",
    "save_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11568890345-SavePromptFunction",
    "add_label": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11568890345-AddLabelFunction"
}

# Initialize AWS Lambda and DynamoDB clients
lambda_client = boto3.client('lambda', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
labels_table = dynamodb.Table('LabelsTable')

# --- Helper Functions ---

def invoke_lambda(function_name, payload):
    """Invoke a specified Lambda function with the provided payload."""
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_ARNS[function_name],
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )
        return json.loads(response["Payload"].read())
    except Exception as e:
        st.error(f"Error calling {function_name} Lambda function: {str(e)}")
        return None

def get_labels():
    """Retrieve existing labels from DynamoDB."""
    try:
        response = labels_table.scan(ConsistentRead=False)
        return {item['label_id']: item['label_name'] for item in response['Items']}
    except Exception as e:
        st.error(f"Error retrieving labels: {str(e)}")
        return {}

def encode_image(file):
    """Encode an uploaded image file as base64."""
    return base64.b64encode(file.read()).decode("utf-8")

# --- Streamlit UI Components ---

st.title("Outpainting Prompt Engineer")

# Outpainting Options
st.subheader("Outpainting Options")
uploaded_image = st.file_uploader("Upload source image for outpainting", type=["png", "jpg", "jpeg"])
outpaint_prompt = st.text_input("Outpainting prompt", "Expand the scene")
seed = st.number_input("Enter seed value (optional):", value=42, min_value=0)
outpaint_width = st.slider("Width of outpainted area", 256, 1024, 512)
outpaint_height = st.slider("Height of outpainted area", 256, 1024, 512)

# Mask Option Selection: User can choose either a mask prompt or a mask image, but not both
mask_option = st.selectbox("Select Mask Option:", ["Use Mask Prompt", "Use Mask Image"])
mask_prompt = None
mask_image_data = None

# Input for the selected mask option
if mask_option == "Use Mask Prompt":
    mask_prompt = st.text_input("Enter Mask Prompt (required)")
elif mask_option == "Use Mask Image":
    uploaded_mask = st.file_uploader("Upload Mask Image (optional)", type=["png", "jpg", "jpeg"])
    if uploaded_mask:
        mask_image_data = encode_image(uploaded_mask)

# Check if the main image is uploaded and at least one mask option is provided
if uploaded_image and (mask_prompt or mask_image_data):
    input_image_data = encode_image(uploaded_image)

    if st.button("Generate Outpainting"):
        # Prepare the outPaintingParams based on the selected mask option
        outpainting_params = {
            "text": outpaint_prompt,
            "image": input_image_data,
            "outPaintingMode": "DEFAULT"  # Allow user to select mode if desired
        }

        # Add the selected mask option to the payload
        if mask_option == "Use Mask Prompt" and mask_prompt:
            outpainting_params["maskPrompt"] = mask_prompt
        elif mask_option == "Use Mask Image" and mask_image_data:
            outpainting_params["maskImage"] = mask_image_data

        # Create the payload
        payload = {
            "taskType": "OUTPAINTING",
            "outPaintingParams": outpainting_params,
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": outpaint_height,
                "width": outpaint_width,
                "cfgScale": 8.0  # You can allow users to adjust this as well
            }
        }

        # Invoke Lambda function
        result = invoke_lambda("outpaint", payload)
        if result and result["statusCode"] == 200:
            st.success("Outpainted image generated successfully!")
            image_data = result.get("image_data")
            image_bytes = base64.b64decode(image_data)
            st.image(Image.open(BytesIO(image_bytes)))
            st.session_state.image_data = image_data
            st.session_state.image_generated = True
        else:
            st.error(result.get("message", "Unknown error"))

else:
    # Display a warning if requirements are not met
    st.warning("Please upload the main image and provide either a mask prompt or a mask image.")

# Rate and Tag Outpainted Image
if st.session_state.get('image_generated', False):
    st.subheader("Rate and Tag the Outpainted Image")
    rating = st.slider("Rate the outpainted image (1-10):", 1, 10, st.session_state.get('rating', 5))

    existing_labels = get_labels()
    selected_labels = st.multiselect("Choose tags for this image:", options=list(existing_labels.values()))

    # Add new label
    new_label = st.text_input("Add a new tag (optional):")
    if st.button("Add Tag") and new_label:
        add_label_result = invoke_lambda("add_label", {"label_name": new_label})
        if add_label_result and add_label_result.get('statusCode') == 200:
            label_data = json.loads(add_label_result['body'])
            existing_labels[label_data['label_id']] = label_data['label_name']
            selected_labels.append(label_data['label_name'])
            st.success(f"Tag '{new_label}' added.")
        else:
            st.error(add_label_result.get("body", "Unknown error"))

    # Convert selected labels to IDs
    selected_label_ids = [label_id for label_id, label_name in existing_labels.items() if label_name in selected_labels]

# Provide Feedback to Optimize Outpainting Prompt
st.subheader("Provide Feedback to Optimize Outpainting Prompt")
feedback_composition = st.text_area("Describe improvements in composition (e.g., layout, balance):")
feedback_lighting = st.text_area("Describe improvements in lighting (e.g., brightness, shadows):")
feedback_style = st.text_area("Describe preferred style adjustments (e.g., realism, abstract):")
feedback_details = st.text_area("Describe key features the outpainted image should have:")
feedback_adjustments = st.text_area("Any other specific adjustments:")

# Optimize Outpainting Prompt
if st.button("Optimize Outpainting Prompt"):
    feedback_payload = {
        "prompt": outpaint_prompt,
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
    result = invoke_lambda("optimize_prompt", feedback_payload)
    if result and result.get('statusCode') == 200:
        st.success("Optimized prompt generated based on your feedback!")
        optimized_prompt = result.get('optimized_prompt')
        st.session_state.optimized_prompt = optimized_prompt
        st.subheader("Optimized Outpainting Prompt")
        st.write(optimized_prompt)
    else:
        st.error(result.get("message", "Unknown error"))

# Save Optimized Prompt
if st.session_state.get('optimized_prompt') or outpaint_prompt:
    prompt_to_save = st.session_state.get('optimized_prompt') or outpaint_prompt
    if st.button("Save Outpainting Prompt"):
        save_payload = {
            "prompt": prompt_to_save,
            "rating": rating,
            "seed": seed,
            "labels": selected_label_ids
        }
        result = invoke_lambda("save_prompt", save_payload)
        if result and result.get('statusCode') == 200:
            st.success("Outpainting prompt saved successfully!")
        else:
            st.error(result.get("message", "Unknown error"))
