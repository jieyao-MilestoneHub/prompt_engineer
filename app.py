import streamlit as st
import boto3
import json
import base64
import uuid
from io import BytesIO
from PIL import Image


lambda_client = boto3.client('lambda', region_name='us-east-1')
st.title("Prompt Engineer")

# 用戶輸入生成圖片
prompt = st.text_input("輸入原始prompt", "A futuristic city at sunset")
seed = st.number_input("輸入種子值(可選):", value=42)

# 初始化 session 狀態
if 'image_generated' not in st.session_state:
    st.session_state.image_generated = False
    st.session_state.image_data = None
    st.session_state.prompt = prompt  # 保存原始 prompt
    st.session_state.optimized_prompt = None
    st.session_state.uuid = str(uuid.uuid4())  # 生成唯一的 UUID

# 創建三個按鈕
col1, col2, col3 = st.columns(3)
with col1:
    generate_image = st.button("生成圖片")
with col2:
    optimize_prompt = st.button("優化提示詞並察看結果")
with col3:
    save_prompt = st.button("保存提示詞")

# 通用的 lambda
lambda_function_name = "arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:ImageProcessingFunction"

# 點擊生成圖片按鈕
if generate_image:
    payload = {
        "prompt": prompt,
        "seed": seed,
        "style": "photography",
        "size": [512, 512]
    }
    try:
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )
        result = json.loads(response['Payload'].read())
        if result.get('statusCode') == 200:
            st.success("圖片生成成功!")
            image_data = result.get('image_data')
            if image_data:
                # 保存圖片數據到 session 狀態
                st.session_state.image_data = image_data
                st.session_state.image_generated = True
                st.session_state.prompt = prompt  # 保存原始提示詞
                st.session_state.optimized_prompt = None  # 重置優化的提示時詞
        else:
            error_message = result.get('error', 'Unknown error')
            st.error(f"圖片生成失敗: {error_message}")
    except Exception as e:
        st.error(f"調用 Lambda 函數時發生錯誤: {str(e)}")

# 點擊優化提示詞並察看結果按鈕
if optimize_prompt:
    # 收集用戶的建議
    suggestion = st.text_area("對於圖片的建議:")
    # 更多反饋

    if suggestion.strip() == "":
        st.error("請提供您的建議以優化提示詞。")
    else:
        feedback_payload = {
            "prompt": st.session_state.prompt,
            "seed": seed,
            "style": "photography",
            "suggestion": suggestion,
            "size": [512, 512]
            # ...
        }
        try:
            response = lambda_client.invoke(
                FunctionName=lambda_function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(feedback_payload)
            )
            result = json.loads(response['Payload'].read())
            if result.get('statusCode') == 200:
                st.success("已經根據您的建議生成新的提示詞！")

                # 更新 session 狀態，更新提示詞與圖片
                st.session_state.image_data = result.get('image_data')
                st.session_state.optimized_prompt = result.get('prompt')
                st.session_state.image_generated = True

                # 顯示新的提示詞
                st.subheader("優化後的提示詞")
                st.write(st.session_state.optimized_prompt)
            else:
                error_message = result.get('error', 'Unknown error')
                st.error(f"處理反饋時出錯: {error_message}")
        except Exception as e:
            st.error(f"調用 Lambda 函數時發生錯誤: {str(e)}")

# 顯示生成的圖片(如果存在)
if st.session_state.image_generated and st.session_state.image_data:
    image_bytes = base64.b64decode(st.session_state.image_data)
    image = Image.open(BytesIO(image_bytes))
    st.image(image)

# 顯示評分滑塊
if st.session_state.image_generated:
    rating = st.slider("為生成的圖片打分 (1-10):", 1, 10, 5)

# 點擊保存提示詞按鈕
if save_prompt:
    if st.session_state.optimized_prompt:
        prompt_to_save = st.session_state.optimized_prompt
    else:
        prompt_to_save = st.session_state.prompt

    save_payload = {
        "uuid": st.session_state.uuid,
        "prompt": prompt_to_save,
        "rating": rating
    }

    # 調用保存提示詞的 Lambda 函數
    try:
        response = lambda_client.invoke(
            FunctionName="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:SavePromptFunction",
            InvocationType="RequestResponse",
            Payload=json.dumps(save_payload)
        )
        result = json.loads(response['Payload'].read())
        if result.get('statusCode') == 200:
            st.success("提示词已成功保存！")
            # 可以在保存後重置狀態或進行其他操作
        else:
            error_message = result.get('message', 'Unknown error')
            st.error(f"保存提示詞出錯: {error_message}")
    except Exception as e:
        st.error(f"調用 Lambda 函數時發生錯誤: {str(e)}")
