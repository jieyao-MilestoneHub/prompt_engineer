# Outpainting Prompt Engineer

Outpainting Prompt Engineer 是一個基於 AWS Lambda 和 Streamlit 的應用，用於生成和優化圖像外展（outpainting）提示（prompt）。此應用允許使用者通過預設尺寸生成圖像，並進一步微調提示以獲得最佳效果。

## 功能

- **圖像生成**：用戶可以上傳主要圖像並選擇使用文字提示（Mask Prompt）或遮罩圖像（Mask Image）來控制圖像外展。
- **尺寸選擇**：提供多種圖像尺寸選項，並包含價格等價提示。
- **提示優化**：用戶可提供反饋，以自動生成經優化的圖像生成提示。
- **評分與標籤**：用戶可以為生成的圖像打分，並添加多個標籤來進行分類。
- **數據持久性**：支持通過 AWS Lambda 和 DynamoDB 保存提示、評分和標籤。

## 主要技術架構

- **前端**：使用 Streamlit 進行快速構建，並為用戶提供交互式 UI。
- **後端**：基於 AWS Lambda，使用 Amazon Titan Image Generator G1 模型處理圖像生成任務，並使用 AWS Bedrock 處理提示優化。
- **存儲**：DynamoDB 儲存生成的提示和標籤，方便管理與查詢。

## 部署

### 先決條件
- 安裝 [AWS CLI](https://docs.aws.amazon.com/zh_tw/cli/latest/userguide/getting-started-install.html)
- 設定 AWS CLI 的憑證及權限
- 安裝 [Python 3.11](https://www.python.org/downloads/) 並確保安裝 Streamlit

### 部署步驟

1. **打包 Lambda 函數**：確保已經將所有 Lambda 函數的程式碼打包並上傳至 S3 存儲桶中（指定於 CloudFormation 模板中）。

2. **CloudFormation 部署**：

    使用以下指令部署 CloudFormation 堆疊：
    ```bash
    aws cloudformation deploy --template-file "$TEMPLATE_FILE" --stack-name "$STACK_NAME" --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
    ```

3. **刪除 CloudFormation 堆疊（選擇性）**：

    若需刪除 CloudFormation 堆疊，使用以下指令：
    ```bash
    aws cloudformation delete-stack --stack-name "$STACK_NAME"
    ```

## 運行本地應用

1. **安裝依賴套件**：
```bash
pip install -r requirements.txt
```

2. **啟動應用**：
```bash
streamlit run app.py
```

3. **訪問應用程序**： 應用將運行在本地伺服器，訪問 http://localhost:8501 以使用界面。

## 使用指南
1. **上傳圖片**：選擇並上傳一張用於外展的源圖像。
2. **選擇遮罩選項**：可選擇遮罩提示（Mask Prompt）或遮罩圖像（Mask Image）來定義外展的範圍。
3. **設置圖片尺寸**：從選單中選擇所需的圖像尺寸和比例。
4. **生成圖像**：點擊“Generate Outpainting”生成圖像。
5. **評分與標籤**：生成圖像後，對其進行評分和標籤。
6. **優化提示**：在提供反饋後，生成優化的提示。
7. **保存結果**：儲存最終提示、評分和標籤。

## 文件結構
```bash
.
├── app.py                  # Streamlit 應用的主程序文件
├── requirements.txt        # Python 依賴項
├── README.md               # 本文件，提供應用文檔
├── cloudformation.yaml     # AWS CloudFormation 模板文件
└── lambda/                 # Lambda 函數代碼目錄
    ├── outpaintImage.py    # 圖像生成 Lambda 函數
    ├── optimizePrompt.py   # 提示優化 Lambda 函數
    └── addLabel.py         # 標籤添加 Lambda 函數
```

## 注意事項
- 確保所有 Lambda 函數和 Streamlit 應用的 ARN、DynamoDB 表等 AWS 資源正確配置在 `app.py` 和 CloudFormation 模板中。
- 刪除 CloudFormation 堆疊會自動刪除所創建的 AWS 資源，包括 Lambda、DynamoDB 表和 IAM Role。此操作不可逆，請謹慎操作。

## 授權

本應用的代碼基於 MIT 授權許可，詳情請參見 [LICENSE](./LICENSE)。