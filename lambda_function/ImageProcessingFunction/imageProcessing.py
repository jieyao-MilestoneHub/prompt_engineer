import boto3
import json
import logging
from botocore.exceptions import ClientError

# 设置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 模型 ID
IMAGE_MODEL_ID = "stability.stable-diffusion-xl-v1"
CLAUDE_MODEL_ID = "anthropic.claude-v2"  # 根据您的实际模型版本进行调整

def lambda_handler(event, context):
    try:
        # 检查是否有建议字段，如果有则处理反馈，否则进行初始图片生成
        if 'suggestion' in event and event['suggestion'].strip():
            # 处理用户反馈并生成优化的图像
            result = process_feedback_and_generate_image(event)
        else:
            # 初始图片生成
            result = generate_initial_image(event)

        return result

    except Exception as e:
        logger.error("Error processing request", exc_info=True)
        return {
            "statusCode": 500,
            "error": str(e)
        }

def generate_initial_image(event):
    # 获取传入的参数
    prompt = event['prompt']
    seed = event.get('seed', 42)
    style = event.get('style', 'photography')
    size = event.get('size', [512, 512])  # 默认大小为 512x512

    # 调用图像生成函数
    image_data = generate_image(prompt, seed, style, size)

    return {
        "statusCode": 200,
        "image_data": image_data,
        "seed": seed,
        "style": style
    }

def process_feedback_and_generate_image(event):
    # 获取原始 prompt、seed 和用户的反馈
    prompt = event.get('prompt')
    seed = event.get('seed', 42)
    style = event.get('style', 'photography')
    suggestion = event.get('suggestion')

    # 构建发送给 Claude 模型的提示词
    assistant_prompt = f"""
原始提示词: {prompt}
用户建议:
{suggestion}

请根据用户的建议，优化原始提示词，使其包含关键因素，生成一个新的图像生成提示词。
"""

    # 调用 AWS Bedrock 的 Claude 模型生成新的提示词
    new_prompt = call_bedrock_claude(assistant_prompt)

    logger.info(f"Optimized prompt: {new_prompt}")

    # 使用新的提示词生成图像
    image_data = generate_image(new_prompt, seed, style)

    return {
        "statusCode": 200,
        "prompt": new_prompt,
        "image_data": image_data,
        "seed": seed
    }

def generate_image(prompt, seed, style, size=[512, 512]):
    """
    调用图像生成服务，返回 base64 编码的图像数据
    """
    # 构建请求体
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1}],
        "height": size[1],
        "width": size[0],
        "cfg_scale": 10,
        "sampler": "k_euler",
        "samples": 1,
        "seed": seed,
        "steps": 50,
        "style_preset": style
    }

    body = json.dumps(payload)

    # 调用图像生成服务（例如 Amazon Bedrock）
    bedrock = boto3.client("bedrock-runtime")
    response = bedrock.invoke_model(
        modelId=IMAGE_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=body
    )

    # 解析响应
    response_body = json.loads(response['body'].read())
    artifact = response_body.get("artifacts")[0]
    base64_image = artifact.get("base64")

    return base64_image

def call_bedrock_claude(prompt):
    """
    调用 AWS Bedrock 的 Claude 模型，生成优化的提示词
    """
    # 创建 Bedrock 客户端
    bedrock = boto3.client('bedrock-runtime')

    # 构建请求体
    payload = {
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.7,
        # 根据需要添加其他参数
    }

    body = json.dumps(payload)

    # 调用 Claude 模型
    response = bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        accept="application/json",
        contentType="application/json",
        body=body
    )

    # 解析响应
    response_body = json.loads(response['body'].read())
    new_prompt = response_body.get('completion').strip()

    return new_prompt
