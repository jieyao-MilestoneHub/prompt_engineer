from aws_client import invoke_lambda

def optimize_prompt(prompt, seed, feedback):
    """Optimize prompt based on user feedback."""
    payload = {
        "prompt": prompt,
        "seed": seed,
        "style": "photographic",
        "suggestion": feedback
    }
    return invoke_lambda("optimize_prompt", payload)
