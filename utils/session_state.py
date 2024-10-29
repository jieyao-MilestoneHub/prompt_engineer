import streamlit as st

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    default_values = {
        'input_image_data': None,
        'uploaded_image_name': None,
        'mask_image_data': None,
        'uploaded_mask_name': None,
        'mask_prompt': None,
        'outpaint_prompt': "Expand the scene",
        'image_data': None,
        'image_generated': False,
        'rating': 5,
        'selected_labels': [],
        'optimized_prompt': None,
        'feedback_composition': '',
        'feedback_lighting': '',
        'feedback_style': '',
        'feedback_details': '',
        'feedback_adjustments': '',
        'selected_dimension_label': None,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
