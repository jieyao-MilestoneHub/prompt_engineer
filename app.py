import streamlit as st
from PIL import Image
from io import BytesIO
import json
from utils.aws_lambda import invoke_lambda
from utils.dynamo_db import get_labels
from utils.image_processing import encode_image, decode_image
from utils.session_state import initialize_session_state
from constants.dimensions import DIMENSIONS_OPTIONS

# Initialize session state
initialize_session_state()

# --- Streamlit UI Components ---

st.title("Outpainting Prompt Engineer")

# Outpainting Options
st.subheader("Outpainting Options")

# Main image upload with session state persistence
uploaded_image = st.file_uploader(
    "Upload source image for outpainting",
    type=["png", "jpg", "jpeg"],
    key='main_image'
)
if uploaded_image is not None:
    st.session_state['input_image_data'] = encode_image(uploaded_image)
    st.session_state['uploaded_image_name'] = uploaded_image.name
elif st.session_state['input_image_data'] is not None:
    st.info(f"Using previously uploaded image: {st.session_state['uploaded_image_name']}")
else:
    st.warning("Please upload a source image for outpainting.")

# Prompt
outpaint_prompt = st.text_input(
    "Outpainting prompt",
    st.session_state['outpaint_prompt']
)
st.session_state['outpaint_prompt'] = outpaint_prompt

# Seed
seed = st.number_input("Enter seed value (optional):", value=42, min_value=0)

# Dimension Selection
dimension_labels = [option['label'] for option in DIMENSIONS_OPTIONS]
if st.session_state['selected_dimension_label'] not in dimension_labels:
    st.session_state['selected_dimension_label'] = dimension_labels[0]

selected_dimension_label = st.selectbox(
    "Select Image Dimensions:",
    dimension_labels,
    index=dimension_labels.index(st.session_state['selected_dimension_label'])
)
st.session_state['selected_dimension_label'] = selected_dimension_label

# Find the selected dimensions
selected_dimension = next(
    (item for item in DIMENSIONS_OPTIONS if item["label"] == selected_dimension_label),
    None
)
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
    mask_prompt = st.text_input(
        "Enter Mask Prompt (required)",
        value=st.session_state.get('mask_prompt', '')
    )
    st.session_state["mask_prompt"] = mask_prompt
    st.session_state["mask_image_data"] = None  # Clear mask image data
elif mask_option == "Use Mask Image":
    uploaded_mask = st.file_uploader(
        "Upload Mask Image (optional)",
        type=["png", "jpg", "jpeg"],
        key='mask_image'
    )
    if uploaded_mask is not None:
        st.session_state['mask_image_data'] = encode_image(uploaded_mask)
        st.session_state['uploaded_mask_name'] = uploaded_mask.name
        st.session_state['mask_prompt'] = None  # Clear mask prompt
    elif st.session_state['mask_image_data'] is not None:
        st.info(f"Using previously uploaded mask image: {st.session_state['uploaded_mask_name']}")
    else:
        st.warning("Please upload a mask image.")

# Check conditions and invoke Lambda function
if st.session_state['input_image_data'] and (
    st.session_state['mask_image_data'] or st.session_state['mask_prompt']
):
    if st.button("Generate Outpainting"):
        # Prepare the payload to match the Lambda function expectations
        payload = {
            "prompt": st.session_state["outpaint_prompt"],
            "input_image_data": st.session_state["input_image_data"],
            "height": int(outpaint_height),
            "width": int(outpaint_width),
            "outPaintingMode": "DEFAULT",
            "seed": seed
        }

        # Add the selected mask option to the payload
        if st.session_state.get("mask_image_data"):
            payload["mask_image_data"] = st.session_state["mask_image_data"]
        elif st.session_state.get("mask_prompt"):
            payload["mask_prompt"] = st.session_state["mask_prompt"]

        # Invoke Lambda function
        result = invoke_lambda("outpaint", payload)
        if result and result.get("statusCode") == 200:
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
    image_bytes = decode_image(st.session_state['image_data'])
    st.image(Image.open(BytesIO(image_bytes)))

    # Rate and Tag Outpainted Image
    st.subheader("Rate and Tag the Outpainted Image")
    rating = st.slider(
        "Rate the outpainted image (1-10):",
        1,
        10,
        st.session_state.get('rating', 5)
    )
    st.session_state['rating'] = rating

    existing_labels = get_labels()
    selected_labels = st.multiselect(
        "Choose tags for this image:",
        options=list(existing_labels.values()),
        default=st.session_state.get('selected_labels', [])
    )
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
            st.error(add_label_result.get("message", "Unknown error"))

    # Convert selected labels to IDs
    selected_label_ids = [
        label_id for label_id, label_name in existing_labels.items()
        if label_name in selected_labels
    ]

    # Provide Feedback to Optimize Outpainting Prompt
    st.subheader("Provide Feedback to Optimize Outpainting Prompt")
    feedback_composition = st.text_area(
        "Describe improvements in composition (e.g., layout, balance):",
        value=st.session_state.get('feedback_composition', '')
    )
    feedback_lighting = st.text_area(
        "Describe improvements in lighting (e.g., brightness, shadows):",
        value=st.session_state.get('feedback_lighting', '')
    )
    feedback_style = st.text_area(
        "Describe preferred style adjustments (e.g., realism, abstract):",
        value=st.session_state.get('feedback_style', '')
    )
    feedback_details = st.text_area(
        "Describe key features the outpainted image should have:",
        value=st.session_state.get('feedback_details', '')
    )
    feedback_adjustments = st.text_area(
        "Any other specific adjustments:",
        value=st.session_state.get('feedback_adjustments', '')
    )

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
                "LabelsIndex": selected_label_ids
            }
            result = invoke_lambda("save_prompt", save_payload)
            if result and result.get('statusCode') == 200:
                st.success("Outpainting prompt saved successfully!")
            else:
                st.error(result.get("message", "Unknown error"))
