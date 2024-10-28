# PowerShell 部署腳本

# 壓縮 Lambda 函數為 .zip 文件
Compress-Archive -Path "C:\Users\USER\Desktop\Develop\prompt_engineer\lambda_function\imageProcessing.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\imageProcessing.zip" -Force
Compress-Archive -Path "C:\Users\USER\Desktop\Develop\prompt_engineer\lambda_function\OptimizePrompt.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\optimizePrompt.zip" -Force
Compress-Archive -Path "C:\Users\USER\Desktop\Develop\prompt_engineer\lambda_function\savePrompt.py" -DestinationPath "C:\Users\USER\Desktop\Develop\prompt_engineer\savePrompt.zip" -Force

# 上傳代碼和層到 S3
$bucketName = "creative360-datateam-image-generator-optimization"
$prefix = "prompt-engineer-manul"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\imageProcessing.zip" "s3://$bucketName/$prefix/lambda/imageProcessing.zip"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\OptimizePrompt.zip" "s3://$bucketName/$prefix/lambda/optimizePrompt.zip"
aws s3 cp "C:\Users\USER\Desktop\Develop\prompt_engineer\savePrompt.zip" "s3://$bucketName/$prefix/lambda/savePrompt.zip"

# 部署 CloudFormation 模板
$timestamp = (Get-Date -Format "yyyyMMddHHmm")
$templateFile = "C:\Users\USER\Desktop\Develop\prompt_engineer\aws-resource\sam-template.yaml"
$stackName = "image-generation-stack-$timestamp"
aws cloudformation deploy --template-file $templateFile --stack-name $stackName --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

Write-Output $stackName
