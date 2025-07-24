#!/usr/bin/env python3
"""
Deploy NutritionGPT Coach v2.1 Fixed to AWS Lambda
Enhanced Memory & Human-like Conversation with Lambda-compatible storage
"""

import os
import sys
import subprocess
import zipfile
import boto3
import json
import tempfile
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def install_dependencies_to_temp():
    """Install dependencies to a temporary directory"""
    print("Installing dependencies to temporary directory...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Using temp directory: {temp_dir}")
    
    # Install packages to temp directory (fixed requirements)
    packages = [
        "openai==1.3.0",
        "langchain==0.1.0", 
        "langchain-openai==0.0.5",
        "requests==2.31.0",
        "boto3==1.34.0",
        "pydantic==2.5.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package} -t {temp_dir}"):
            return None
    
    return temp_dir

def create_deployment_package(temp_dir):
    """Create the deployment package"""
    print("Creating deployment package...")
    
    # Files to include
    files_to_include = [
        "nutrition_coach_v2_1_fixed.py",
        "requirements_fixed.txt"
    ]
    
    # Create zip file
    with zipfile.ZipFile("nutrition_coach_v2_1_fixed.zip", "w") as zipf:
        # Add main files
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file} to package")
        
        # Add all installed packages from temp directory
        if temp_dir and os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith((".py", ".so", ".dll", ".dylib")):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
                        print(f"Added package: {arcname}")
    
    print("Deployment package created: nutrition_coach_v2_1_fixed.zip")
    return True

def deploy_to_lambda():
    """Deploy to AWS Lambda"""
    print("Deploying to AWS Lambda...")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda')
    
    # Function configuration
    function_name = "NutritionGPTBot-v2-1-Fixed"
    runtime = "python3.11"
    handler = "nutrition_coach_v2_1_fixed.lambda_handler"
    timeout = 30
    memory_size = 512
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"Function {function_name} exists, updating...")
            
            # Update function code
            with open("nutrition_coach_v2_1_fixed.zip", "rb") as f:
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=f.read()
                )
            
            # Update function configuration
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime=runtime,
                Handler=handler,
                Timeout=timeout,
                MemorySize=memory_size,
                Environment={
                    'Variables': {
                        'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
                        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')
                    }
                }
            )
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"Function {function_name} does not exist, creating...")
            
            # Create function
            with open("nutrition_coach_v2_1_fixed.zip", "rb") as f:
                lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime=runtime,
                    Handler=handler,
                    Role="arn:aws:iam::123456789012:role/lambda-execution-role",  # Update with your role
                    Code={'ZipFile': f.read()},
                    Timeout=timeout,
                    MemorySize=memory_size,
                    Environment={
                        'Variables': {
                            'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
                            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')
                        }
                    }
                )
        
        print(f"Successfully deployed {function_name} to AWS Lambda!")
        
        # Get function URL
        try:
            response = lambda_client.get_function_url_config(FunctionName=function_name)
            webhook_url = response['FunctionUrl']
            print(f"Webhook URL: {webhook_url}")
        except:
            print("Function URL not configured. You may need to create one manually.")
        
        return True
        
    except Exception as e:
        print(f"Error deploying to Lambda: {e}")
        return False

def setup_webhook():
    """Setup Telegram webhook"""
    print("Setting up Telegram webhook...")
    
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        print("TELEGRAM_BOT_TOKEN not set, skipping webhook setup")
        return False
    
    # Get function URL
    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.get_function_url_config(FunctionName="NutritionGPTBot-v2-1-Fixed")
        webhook_url = response['FunctionUrl']
        
        # Set webhook
        webhook_setup_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook?url={webhook_url}/webhook"
        
        import requests
        response = requests.get(webhook_setup_url)
        if response.status_code == 200:
            print("Webhook set successfully!")
            return True
        else:
            print(f"Failed to set webhook: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error setting webhook: {e}")
        return False

def cleanup_temp_dir(temp_dir):
    """Clean up temporary directory"""
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {e}")

def main():
    """Main deployment process"""
    print("🚀 Starting NutritionGPT Coach v2.1 Fixed Deployment")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {missing_vars}")
        print("Please set these before running the deployment.")
        return False
    
    temp_dir = None
    try:
        # Step 1: Install dependencies to temp directory
        temp_dir = install_dependencies_to_temp()
        if not temp_dir:
            print("❌ Failed to install dependencies")
            return False
        
        # Step 2: Create deployment package
        if not create_deployment_package(temp_dir):
            print("❌ Failed to create deployment package")
            return False
        
        # Step 3: Deploy to Lambda
        if not deploy_to_lambda():
            print("❌ Failed to deploy to Lambda")
            return False
        
        # Step 4: Setup webhook
        setup_webhook()
        
        print("✅ Deployment completed successfully!")
        print("\n🎉 NutritionGPT Coach v2.1 Fixed is now live!")
        print("\nKey Improvements:")
        print("- Lambda-compatible memory system using DynamoDB/S3")
        print("- Removed ChromaDB dependency for better Lambda compatibility")
        print("- Enhanced error handling and fallback mechanisms")
        print("- More human-like, conversational responses")
        print("- Better context awareness and personalization")
        print("- Improved user profile management")
        
        return True
        
    finally:
        # Always clean up temp directory
        cleanup_temp_dir(temp_dir)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 