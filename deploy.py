#!/usr/bin/env python3
"""
AWS Lambda Deployment Script for NutritionGPT Bot
"""
import os
import shutil
import subprocess
import zipfile
import boto3
import json
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for AWS Lambda"""
    print("📦 Creating deployment package...")
    
    # Create deployment directory
    deploy_dir = "deployment"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy source files
    source_files = [
        "lambda_function.py",
        "bot_fixed.py", 
        "ai_service.py",
        "config.py",
        "requirements.txt"
    ]
    
    for file in source_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"✅ Copied {file}")
    
    # Install dependencies
    print("📥 Installing dependencies...")
    subprocess.run([
        "pip", "install", "-r", "requirements.txt", 
        "-t", deploy_dir, "--platform", "manylinux2014_x86_64",
        "--only-binary=all"
    ], check=True)
    
    # Create ZIP file
    zip_name = "nutritiongpt-lambda.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created deployment package: {zip_name}")
    return zip_name

def deploy_to_lambda(function_name="NutritionGPTBot", zip_file="nutritiongpt-lambda.zip"):
    """Deploy the package to AWS Lambda"""
    print(f"🚀 Deploying to AWS Lambda function: {function_name}")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda')
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"📝 Updating existing function: {function_name}")
            
            # Update function code
            with open(zip_file, 'rb') as f:
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=f.read()
                )
            
            # Update function configuration
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime='python3.12',
                Handler='lambda_function.lambda_handler',
                Timeout=30,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
                        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
                    }
                }
            )
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"🆕 Creating new function: {function_name}")
            
            # Create new function
            with open(zip_file, 'rb') as f:
                lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.12',
                    Role='arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role',  # You'll need to create this
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': f.read()},
                    Description='NutritionGPT Telegram Bot',
                    Timeout=30,
                    MemorySize=512,
                    Environment={
                        'Variables': {
                            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
                            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
                        }
                    }
                )
        
        print(f"✅ Successfully deployed to {function_name}")
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def set_webhook_url(function_name="NutritionGPTBot"):
    """Set the Telegram webhook URL to point to the Lambda function"""
    print("🔗 Setting up Telegram webhook...")
    
    # Get function URL
    lambda_client = boto3.client('lambda')
    
    try:
        # Create function URL if it doesn't exist
        try:
            lambda_client.get_function_url_config(FunctionName=function_name)
        except lambda_client.exceptions.ResourceNotFoundException:
            lambda_client.create_function_url_config(
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
        
        # Get the function URL
        response = lambda_client.get_function_url_config(FunctionName=function_name)
        function_url = response['FunctionUrl']
        
        print(f"📱 Function URL: {function_url}")
        
        # Set Telegram webhook
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        import requests
        webhook_data = {
            'url': function_url,
            'allowed_updates': ['message', 'callback_query']
        }
        
        response = requests.post(webhook_url, json=webhook_data)
        
        if response.status_code == 200:
            print("✅ Webhook set successfully!")
            return function_url
        else:
            print(f"❌ Failed to set webhook: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return None

def main():
    """Main deployment function"""
    print("🤖 NutritionGPT Bot - AWS Lambda Deployment")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Please set them in your environment or .env file")
        return False
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Deploy to Lambda
    if deploy_to_lambda(zip_file=zip_file):
        # Set webhook
        function_url = set_webhook_url()
        if function_url:
            print("\n🎉 Deployment successful!")
            print(f"📱 Your bot is now running at: {function_url}")
            print("💡 Test your bot on Telegram!")
            return True
    
    return False

if __name__ == "__main__":
    main() 