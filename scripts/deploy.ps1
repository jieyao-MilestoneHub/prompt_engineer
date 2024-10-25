# PowerShell 部署腳本

# 設定 Lambda 函數文件夾路徑
$lambdaFolderPath = "C:\Users\USER\Desktop\Develop\prompt_engineer\lambda_functions"

# 設定工作目錄
Set-Location -Path $lambdaFolderPath

# 壓縮 Lambda 函數為 .zip 文件
Compress-Archive -Path "generateImage.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\generate_image.zip" -Force
Compress-Archive -Path "saveFeedback.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\save_feedback.zip" -Force
Compress-Archive -Path "adjustPrompt.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\adjust_prompt.zip" -Force
Compress-Archive -Path "collectFeeback.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\collect_feedback.zip" -Force

# 上傳代碼和層到 S3
$bucketName = "creative360-datateam-image-generator-optimization"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\generate_image.zip" "s3://$bucketName/prompt-engineer-manul/lambda/generate_image.zip"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\save_feedback.zip" "s3://$bucketName/prompt-engineer-manul/lambda/save_feedback.zip"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\adjust_prompt.zip" "s3://$bucketName/prompt-engineer-manul/lambda/adjust_prompt.zip"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\collect_feedback.zip" "s3://$bucketName/prompt-engineer-manul/lambda/collect_feedback.zip"

# 上傳 step function 設定檔到 S3
aws s3 cp "step_function/state_machine.json" "s3://$bucketName/prompt-engineer-manul/lambda/state_machine.json"

# 部署 CloudFormation 模板
$templateFile = "C:\Users\USER\Desktop\Develop\prompt_engineer\templates\cloudformation.yaml"
$stackName = "image-generation-stack"
aws cloudformation deploy --template-file $templateFile --stack-name $stackName --capabilities CAPABILITY_IAM

Write-Host "部署完成！"
