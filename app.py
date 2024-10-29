import streamlit as st
import boto3
import json
import base64
from io import BytesIO
from PIL import Image

# --- AWS Lambda Configuration ---
LAMBDA_ARNS = {
    "outpaint": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569101544-OutpaintFunction",
    "optimize_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569101544-OptimizePromptFunction",
    "save_prompt": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569101544-SavePromptFunction",
    "add_label": "arn:aws:lambda:us-east-1:992382611204:function:image-generation-stack-11569101544-AddLabelFunction"
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

# --- Predefined Dimensions and Aspect Ratios ---

dimensions_options = [
    {"label": "1024 x 1024 (1:1) - Price: Equivalent to 1024 x 1024", "width": 1024, "height": 1024},
    {"label": "768 x 768 (1:1) - Price: Equivalent to 512 x 512", "width": 768, "height": 768},
    {"label": "512 x 512 (1:1) - Price: Equivalent to 512 x 512", "width": 512, "height": 512},
    {"label": "768 x 1152 (2:3) - Price: Equivalent to 1024 x 1024", "width": 768, "height": 1152},
    {"label": "384 x 576 (2:3) - Price: Equivalent to 512 x 512", "width": 384, "height": 576},
    {"label": "1152 x 768 (3:2) - Price: Equivalent to 1024 x 1024", "width": 1152, "height": 768},
    {"label": "576 x 384 (3:2) - Price: Equivalent to 512 x 512", "width": 576, "height": 384},
    {"label": "768 x 1280 (3:5) - Price: Equivalent to 1024 x 1024", "width": 768, "height": 1280},
    {"label": "384 x 640 (3:5) - Price: Equivalent to 512 x 512", "width": 384, "height": 640},
    {"label": "1280 x 768 (5:3) - Price: Equivalent to 1024 x 1024", "width": 1280, "height": 768},
    {"label": "640 x 384 (5:3) - Price: Equivalent to 512 x 512", "width": 640, "height": 384},
    {"label": "896 x 1152 (7:9) - Price: Equivalent to 1024 x 1024", "width": 896, "height": 1152},
    {"label": "448 x 576 (7:9) - Price: Equivalent to 512 x 512", "width": 448, "height": 576},
    {"label": "1152 x 896 (9:7) - Price: Equivalent to 1024 x 1024", "width": 1152, "height": 896},
    {"label": "576 x 448 (9:7) - Price: Equivalent to 512 x 512", "width": 576, "height": 448},
    {"label": "768 x 1408 (6:11) - Price: Equivalent to 1024 x 1024", "width": 768, "height": 1408},
    {"label": "384 x 704 (6:11) - Price: Equivalent to 512 x 512", "width": 384, "height": 704},
    {"label": "1408 x 768 (11:6) - Price: Equivalent to 1024 x 1024", "width": 1408, "height": 768},
    {"label": "704 x 384 (11:6) - Price: Equivalent to 512 x 512", "width": 704, "height": 384},
    {"label": "640 x 1408 (5:11) - Price: Equivalent to 1024 x 1024", "width": 640, "height": 1408},
    {"label": "320 x 704 (5:11) - Price: Equivalent to 512 x 512", "width": 320, "height": 704},
    {"label": "1408 x 640 (11:5) - Price: Equivalent to 1024 x 1024", "width": 1408, "height": 640},
    {"label": "704 x 320 (11:5) - Price: Equivalent to 512 x 512", "width": 704, "height": 320},
    {"label": "1152 x 640 (9:5) - Price: Equivalent to 1024 x 1024", "width": 1152, "height": 640},
    {"label": "1173 x 640 (16:9) - Price: Equivalent to 1024 x 1024", "width": 1173, "height": 640},
]

# --- Streamlit UI Components ---

st.title("Outpainting Prompt Engineer")

# Initialize session state variables if they don't exist
if 'input_image_data' not in st.session_state:
    st.session_state['input_image_data'] = None
    st.session_state['uploaded_image_name'] = None

if 'mask_image_data' not in st.session_state:
    st.session_state['mask_image_data'] = None
    st.session_state['uploaded_mask_name'] = None

if 'mask_prompt' not in st.session_state:
    st.session_state['mask_prompt'] = None

if 'outpaint_prompt' not in st.session_state:
    st.session_state['outpaint_prompt'] = "Expand the scene"

if 'image_data' not in st.session_state:
    st.session_state['image_data'] = None
    st.session_state['image_generated'] = False

if 'rating' not in st.session_state:
    st.session_state['rating'] = 5

if 'selected_labels' not in st.session_state:
    st.session_state['selected_labels'] = []

if 'optimized_prompt' not in st.session_state:
    st.session_state['optimized_prompt'] = None

# Outpainting Options
st.subheader("Outpainting Options")

# Main image upload with session state persistence
uploaded_image = st.file_uploader("Upload source image for outpainting", type=["png", "jpg", "jpeg"], key='main_image')
if uploaded_image is not None:
    st.session_state['input_image_data'] = encode_image(uploaded_image)
    st.session_state['uploaded_image_name'] = uploaded_image.name
elif st.session_state['input_image_data'] is not None:
    st.info(f"Using previously uploaded image: {st.session_state['uploaded_image_name']}")
else:
    st.warning("Please upload a source image for outpainting.")

# Prompt
outpaint_prompt = st.text_input("Outpainting prompt", st.session_state['outpaint_prompt'])
st.session_state['outpaint_prompt'] = outpaint_prompt

# Seed
seed = st.number_input("Enter seed value (optional):", value=42, min_value=0)

# Dimension Selection
dimension_labels = [option['label'] for option in dimensions_options]
selected_dimension_label = st.selectbox("Select Image Dimensions:", dimension_labels)
# Find the selected dimensions
selected_dimension = next((item for item in dimensions_options if item["label"] == selected_dimension_label), None)
if selected_dimension:
    outpaint_width = selected_dimension['width']
    outpaint_height = selected_dimension['height']
else:
    # Default dimensions
    outpaint_width = 512
    outpaint_height = 512

# Mask Option Selection
mask_option = st.selectbox("Select Mask Option:", ["Use Mask Prompt", "Use Mask Image"])
if mask_option == "Use Mask Prompt":
    mask_prompt = st.text_input("Enter Mask Prompt (required)", value=st.session_state.get('mask_prompt', ''))
    st.session_state["mask_prompt"] = mask_prompt
    st.session_state["mask_image_data"] = None  # Clear mask image data
elif mask_option == "Use Mask Image":
    uploaded_mask = st.file_uploader("Upload Mask Image (optional)", type=["png", "jpg", "jpeg"], key='mask_image')
    if uploaded_mask is not None:
        st.session_state['mask_image_data'] = encode_image(uploaded_mask)
        st.session_state['uploaded_mask_name'] = uploaded_mask.name
        st.session_state['mask_prompt'] = None  # Clear mask prompt
    elif st.session_state['mask_image_data'] is not None:
        st.info(f"Using previously uploaded mask image: {st.session_state['uploaded_mask_name']}")
    else:
        st.warning("Please upload a mask image.")

# Check conditions and invoke Lambda function
if st.session_state['input_image_data'] and (st.session_state['mask_image_data'] or st.session_state['mask_prompt']):
    if st.button("Generate Outpainting"):
        # Prepare the payload to match the Lambda function expectations
        payload = {
            "prompt": st.session_state["outpaint_prompt"],
            "input_image_data": st.session_state["input_image_data"],
            "height": int(outpaint_height),
            "width": int(outpaint_width),
            "outPaintingMode": "DEFAULT"
        }

        # Add the selected mask option to the payload
        if st.session_state.get("mask_image_data"):
            payload["mask_image_data"] = st.session_state["mask_image_data"]
        elif st.session_state.get("mask_prompt"):
            payload["mask_prompt"] = st.session_state["mask_prompt"]

        # Invoke Lambda function
        result = invoke_lambda("outpaint", payload)
        if result and result["statusCode"] == 200:
            st.success("Outpainted image generated successfully!")
            image_data = result.get("image_data")
            st.session_state['image_data'] = image_data
            st.session_state['image_generated'] = True
        else:
            st.error(result.get("message", "Unknown error"))
else:
    # Display a warning if requirements are not met
    st.warning("Please upload the main image and provide either a mask prompt or a mask image.")

# Display the generated image if available
if st.session_state.get('image_generated', False) and st.session_state.get('image_data'):
    st.subheader("Generated Outpainted Image")
    image_bytes = base64.b64decode(st.session_state['image_data'])
    st.image(Image.open(BytesIO(image_bytes)))

    # Rate and Tag Outpainted Image
    st.subheader("Rate and Tag the Outpainted Image")
    rating = st.slider("Rate the outpainted image (1-10):", 1, 10, st.session_state.get('rating', 5))
    st.session_state['rating'] = rating

    existing_labels = get_labels()
    selected_labels = st.multiselect("Choose tags for this image:", options=list(existing_labels.values()), default=st.session_state.get('selected_labels', []))
    st.session_state['selected_labels'] = selected_labels

    # Add new label
    new_label = st.text_input("Add a new tag (optional):")
    if st.button("Add Tag") and new_label:
        add_label_result = invoke_lambda("add_label", {"label_name": new_label})
        if add_label_result and add_label_result.get('statusCode') == 200:
            label_data = json.loads(add_label_result['body'])
            existing_labels[label_data['label_id']] = label_data['label_name']
            selected_labels.append(label_data['label_name'])
            st.session_state['selected_labels'] = selected_labels
            st.success(f"Tag '{new_label}' added.")
        else:
            st.error(add_label_result.get("body", "Unknown error"))

    # Convert selected labels to IDs
    selected_label_ids = [label_id for label_id, label_name in existing_labels.items() if label_name in selected_labels]

    # Provide Feedback to Optimize Outpainting Prompt
    st.subheader("Provide Feedback to Optimize Outpainting Prompt")
    feedback_composition = st.text_area("Describe improvements in composition (e.g., layout, balance):", value=st.session_state.get('feedback_composition', ''))
    feedback_lighting = st.text_area("Describe improvements in lighting (e.g., brightness, shadows):", value=st.session_state.get('feedback_lighting', ''))
    feedback_style = st.text_area("Describe preferred style adjustments (e.g., realism, abstract):", value=st.session_state.get('feedback_style', ''))
    feedback_details = st.text_area("Describe key features the outpainted image should have:", value=st.session_state.get('feedback_details', ''))
    feedback_adjustments = st.text_area("Any other specific adjustments:", value=st.session_state.get('feedback_adjustments', ''))

    # Store feedback in session state
    st.session_state['feedback_composition'] = feedback_composition
    st.session_state['feedback_lighting'] = feedback_lighting
    st.session_state['feedback_style'] = feedback_style
    st.session_state['feedback_details'] = feedback_details
    st.session_state['feedback_adjustments'] = feedback_adjustments

    # Optimize Outpainting Prompt
    if st.button("Optimize Outpainting Prompt"):
        feedback_payload = {
            "prompt": st.session_state.get('outpaint_prompt', ''),
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
            st.session_state['optimized_prompt'] = optimized_prompt
            st.subheader("Optimized Outpainting Prompt")
            st.write(optimized_prompt)
        else:
            st.error(result.get("message", "Unknown error"))

    # Save Optimized Prompt
    if st.session_state.get('optimized_prompt') or st.session_state.get('outpaint_prompt'):
        prompt_to_save = st.session_state.get('optimized_prompt') or st.session_state.get('outpaint_prompt')
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
