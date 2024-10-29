from aws_client import invoke_lambda

def generate_image(prompt, seed, style="photographic"):
    """Generate an image with the specified prompt and seed."""
    payload = {
        "prompt": prompt,
        "seed": seed,
        "style": style
    }
    return invoke_lambda("image_generator", payload)

def generate_outpainting(outpaint_prompt, input_image_data, mask_image_data, width, height):
    """Generate an outpainted image using the outpainting Lambda function."""
    payload = {
        "prompt": outpaint_prompt,
        "input_image_data": input_image_data,
        "mask_image_data": mask_image_data,
        "width": width,
        "height": height
    }
    return invoke_lambda("outpaint", payload)
