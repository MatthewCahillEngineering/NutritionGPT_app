#!/usr/bin/env python3
"""
Deployment script for NutritionGPT Telegram Bot
Deploys to AWS Lambda with DynamoDB
"""

import boto3
import json
import zipfile
import os
import sys
from botocore.exceptions import ClientError

def create_deployment_package():
    """Create a ZIP file for Lambda deployment"""
    print("📦 Creating deployment package...")
    
    # Files to include in the package
    files_to_include = [
        'bot.py',
        'config.py',
        'database.py',
        'ai_service.py',
        'lambda_function.py',
        'requirements.txt'
    ]
    
    # Create ZIP file
    with zipfile.ZipFile('nutrition_bot.zip', 'w') as zipf:
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  ✅ Added {file}")
            else:
                print(f"  ❌ Missing {file}")
    
    print("✅ Deployment package created: nutrition_bot.zip")
    return 'nutrition_bot.zip'

def create_iam_role():
    """Create IAM role for Lambda function"""
    print("🔐 Creating IAM role...")
    
    iam = boto3.client('iam')
    role_name = 'NutritionBotLambdaRole'
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permission policy
    permission_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:CreateTable",
                    "dynamodb:DescribeTable"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/nutrition_tracker"
            }
        ]
    }
    
    try:
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for NutritionGPT Lambda function'
        )
        
        # Attach permission policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='NutritionBotPolicy',
            PolicyDocument=json.dumps(permission_policy)
        )
        
        # Attach basic Lambda execution role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ IAM role created: {role_name}")
        return response['Role']['Arn']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"✅ IAM role already exists: {role_name}")
            return f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:role/{role_name}"
        else:
            print(f"❌ Error creating IAM role: {e}")
            return None

def deploy_lambda_function(zip_file, role_arn):
    """Deploy Lambda function"""
    print("🚀 Deploying Lambda function...")
    
    lambda_client = boto3.client('lambda')
    function_name = 'NutritionGPTBot'
    
    try:
        # Read ZIP file
        with open(zip_file, 'rb') as f:
            zip_content = f.read()
        
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print("📝 Updating existing function...")
            
            # Update function code
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
            # Update function configuration
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime='python3.9',
                Handler='lambda_function.lambda_handler',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                        'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
                        'DYNAMODB_TABLE_NAME': 'nutrition_tracker'
                    }
                }
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("🆕 Creating new function...")
                
                # Create function
                lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role=role_arn,
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': zip_content},
                    Description='NutritionGPT Telegram Bot',
                    Timeout=30,
                    MemorySize=256,
                    Environment={
                        'Variables': {
                            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                            'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
                            'DYNAMODB_TABLE_NAME': 'nutrition_tracker'
                        }
                    }
                )
            else:
                raise e
        
        print(f"✅ Lambda function deployed: {function_name}")
        return function_name
        
    except Exception as e:
        print(f"❌ Error deploying Lambda function: {e}")
        return None

def setup_webhook(function_name):
    """Setup Telegram webhook"""
    print("🔗 Setting up Telegram webhook...")
    
    # Get function URL
    lambda_client = boto3.client('lambda')
    
    try:
        # Create function URL
        response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['*'],
                'AllowMethods': ['*'],
                'AllowOrigins': ['*'],
                'ExposeHeaders': ['*'],
                'MaxAge': 86400
            }
        )
        
        webhook_url = response['FunctionUrl']
        print(f"✅ Function URL: {webhook_url}")
        
        # Set Telegram webhook
        import requests
        telegram_token = "8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc"
        webhook_setup_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
        
        webhook_response = requests.post(webhook_setup_url, json={
            'url': webhook_url
        })
        
        if webhook_response.status_code == 200:
            print("✅ Telegram webhook set successfully!")
        else:
            print(f"❌ Error setting webhook: {webhook_response.text}")
        
        return webhook_url
        
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")
        return None

def main():
    """Main deployment function"""
    print("🚀 Starting NutritionGPT Bot Deployment...")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it: export OPENAI_API_KEY=your_key_here")
        return
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Create IAM role
    role_arn = create_iam_role()
    if not role_arn:
        print("❌ Failed to create IAM role")
        return
    
    # Deploy Lambda function
    function_name = deploy_lambda_function(zip_file, role_arn)
    if not function_name:
        print("❌ Failed to deploy Lambda function")
        return
    
    # Setup webhook
    webhook_url = setup_webhook(function_name)
    
    print("\n🎉 Deployment completed successfully!")
    print(f"📱 Your bot is now live at: t.me/NutritionGPTAI_bot")
    print(f"🔗 Webhook URL: {webhook_url}")
    print("\n💡 Test your bot by sending /start to @NutritionGPTAI_bot")

if __name__ == "__main__":
    main() 