# Outpainting Prompt Engineer

The Outpainting Prompt Engineer repository is designed for those interested in collecting, optimizing, and managing prompts for image outpainting tasks. This application offers a straightforward implementation for generating, optimizing, and storing prompts along with prompt tags in DynamoDB, making it ideal for downstream applications that require a database of refined image generation prompts.

## Purpose

This repository enables users to:

- Generate outpainting prompts using AWS Lambda with Streamlit as the UI.
- Collect and refine prompts for better performance in image expansion tasks.
- Store generated prompts, ratings, and tags in DynamoDB for organized management and future use.

## Features

- **Image Generation**: Users can upload a main image and choose to use a text prompt (Mask Prompt) or a mask image (Mask Image) to control the outpainting area.
- **Dimension Selection**: Provides multiple image dimension options, along with equivalent pricing indications.
- **Prompt Optimization**: Users can provide feedback to automatically generate optimized prompts for image generation.
- **Rating and Tagging**: Users can rate generated images and add multiple tags for categorization.
- **Data Persistence**: Supports prompt, rating, and tag storage via AWS Lambda and DynamoDB.

## Technical Architecture

- **Frontend**: Built with Streamlit to provide a quick, interactive UI for users.
- **Backend**: Powered by AWS Lambda, utilizing the Amazon Titan Image Generator G1 model for image generation tasks and AWS Bedrock for prompt optimization.
- **Storage**: DynamoDB stores generated prompts and tags for easy management and querying.

## Deployment

### Prerequisites
- Install [AWS CLI](https://docs.aws.amazon.com/zh_tw/cli/latest/userguide/getting-started-install.html)
- Configure credentials and permissions for AWS CLI
- Install [Python 3.11](https://www.python.org/downloads/) and ensure Streamlit is installed

### Deployment Steps

1. **Package Lambda Functions**: Ensure all Lambda function code is packaged and uploaded to the designated S3 bucket specified in the CloudFormation template.

2. **CloudFormation Deployment**:

    Deploy the CloudFormation stack using the following command:
    ```bash
    aws cloudformation deploy --template-file "$TEMPLATE_FILE" --stack-name "$STACK_NAME" --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
    ```

3. **Delete CloudFormation Stack (Optional):**：

    To delete the CloudFormation stack, use the following command:
    ```bash
    aws cloudformation delete-stack --stack-name "$STACK_NAME"
    ```

### Running the Application Locally

1. **Install Dependencies**：
```bash
pip install -r requirements.txt
```

2. **Start the Application**：
```bash
streamlit run app.py
```

3. **Access the Application**: The app will run on a local server at `http://localhost:8501`.

## Usage Guide

1. **Upload Image**: Select and upload an image for outpainting.
2. **Select Mask Option**: Choose either Mask Prompt or Mask Image to define the outpainting area.
3. **Set Image Dimensions**: Choose desired dimensions and aspect ratio from the menu.
4. **Generate Image**: Click “Generate Outpainting” to create the image.
5. **Rate and Tag**: After generating the image, rate it and apply relevant tags.
6. **Optimize Prompt**: Provide feedback to generate an optimized prompt.
7. **Save Results**: Save the final prompt, rating, and tags.

## Project Structure
```bash
.
├── app.py                     # Main Streamlit app file
├── config.py                  # Configuration file for application settings
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation file for app overview and instructions
├── LICENSE                    # License file, detailing usage rights
├── .gitignore                 # Git ignore file for excluding unnecessary files from version control

├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions workflow for CI/CD pipeline

├── aws-resource/
│   └── sam-template.yaml      # AWS SAM/CloudFormation template for defining AWS resources

├── constants/
│   └── dimensions.py          # Module for image dimension constants used in the application

├── lambda_function/           # Directory for Lambda functions code
│   ├── addLabel.py            # Lambda function for adding labels
│   ├── imageProcessing.py      # Lambda function for processing images
│   ├── optimizePrompt.py       # Lambda function for optimizing prompts
│   ├── outpaintImage.py        # Lambda function for generating outpainted images
│   └── savePrompt.py           # Lambda function for saving prompts

├── scripts/                   # Directory for deployment scripts
│   ├── deploy.ps1             # PowerShell script for deploying the application
│   └── deploy.sh              # Bash script for deploying the application

└── utils/                     # Utility modules for additional app functionality
    ├── aws_lambda.py          # Helper functions for invoking AWS Lambda
    ├── dynamo_db.py           # Helper functions for interacting with DynamoDB
    ├── image_processing.py    # Helper functions for image processing
    └── session_state.py       # Helper functions for managing Streamlit session state

```

## Notes
- Ensure all AWS resources, including Lambda ARNs, DynamoDB tables, and IAM roles, are correctly configured in both `app.py` and the CloudFormation template.
- Deleting the CloudFormation stack will remove all created AWS resources, including Lambda, DynamoDB tables, and IAM roles. This action is irreversible; proceed with caution.

## License
This application’s code is licensed under the MIT License. For details, see [LICENSE](./LICENSE).