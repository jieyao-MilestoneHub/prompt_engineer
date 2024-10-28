#!/bin/bash

# 定義參數
BUCKET_NAME="creative360-datateam-image-generator-optimization"
PREFIX="prompt-engineer-manul"
TIMESTAMP=$(date +"%Y%m%d%H%M")
TEMPLATE_FILE="aws-resource/sam-template.yaml"
STACK_NAME="image-generation-stack-$TIMESTAMP"

# Lambda 壓縮並上傳至 S3
echo "Zipping and uploading Lambda functions to S3..."

# 壓縮 Lambda 函數為 .zip 文件
zip -j "imageProcessing.zip" "C:/Users/USER/Desktop/Develop/prompt_engineer/lambda_function/imageProcessing.py"
zip -j "optimizePrompt.zip" "C:/Users/USER/Desktop/Develop/prompt_engineer/lambda_function/OptimizePrompt.py"
zip -j "savePrompt.zip" "C:/Users/USER/Desktop/Develop/prompt_engineer/lambda_function/savePrompt.py"
zip -j "addLabel.zip" "C:/Users/USER/Desktop/Develop/prompt_engineer/lambda_function/addLabel.py"

# 上傳至 S3
aws s3 cp "imageProcessing.zip" "s3://$BUCKET_NAME/$PREFIX/lambda/imageProcessing.zip"
aws s3 cp "optimizePrompt.zip" "s3://$BUCKET_NAME/$PREFIX/lambda/optimizePrompt.zip"
aws s3 cp "savePrompt.zip" "s3://$BUCKET_NAME/$PREFIX/lambda/savePrompt.zip"
aws s3 cp "addLabel.zip" "s3://$BUCKET_NAME/$PREFIX/lambda/addLabel.zip"

# 部署 CloudFormation 模板
echo "Deploying CloudFormation stack: $STACK_NAME"
aws cloudformation deploy --template-file "$TEMPLATE_FILE" --stack-name "$STACK_NAME" --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

# 結束並顯示 stack name
echo "Deployment completed. Stack name: $STACK_NAME"
