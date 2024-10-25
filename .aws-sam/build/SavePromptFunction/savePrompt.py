import boto3
from datetime import datetime

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SavedPrompts')

    # 获取数据
    prompt = event.get('prompt')
    rating = event.get('rating')
    uuid_value = event.get('uuid')

    # 创建数据项
    item = {
        'uuid': uuid_value,
        'prompt': prompt,
        'rating': str(rating),
        'timestamp': datetime.utcnow().isoformat()
    }

    # 保存到 DynamoDB
    try:
        table.put_item(Item=item)
        return {
            "statusCode": 200,
            "message": "提示词已成功保存。"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "message": f"保存提示词时出错：{str(e)}"
        }
