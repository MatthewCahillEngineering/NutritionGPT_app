#!/usr/bin/env python3
"""
Deploy NutritionGPT Coach v2.1 to AWS Lambda
Enhanced memory and human-like conversation
"""

import os
import sys
import subprocess
import zipfile
import boto3
import json
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

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    # Install packages
    packages = [
        "openai==1.3.0",
        "langchain==0.1.0", 
        "langchain-openai==0.0.5",
        "chromadb==0.4.18",
        "requests==2.31.0",
        "boto3==1.34.0",
        "pydantic==2.5.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package} -t ."):
            return False
    
    return True

def create_deployment_package():
    """Create the deployment package"""
    print("Creating deployment package...")
    
    # Files to include
    files_to_include = [
        "nutrition_coach_v2_1.py",
        "requirements.txt"
    ]
    
    # Create zip file
    with zipfile.ZipFile("nutrition_coach_v2_1.zip", "w") as zipf:
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file} to package")
        
        # Add all installed packages
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith((".py", ".so", ".dll", ".dylib")):
                    file_path = os.path.join(root, file)
                    if not file_path.startswith("./__pycache__"):
                        zipf.write(file_path)
    
    print("Deployment package created: nutrition_coach_v2_1.zip")
    return True

def deploy_to_lambda():
    """Deploy to AWS Lambda"""
    print("Deploying to AWS Lambda...")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda')
    
    # Function configuration
    function_name = "NutritionGPTBot-v2-1"
    runtime = "python3.11"
    handler = "nutrition_coach_v2_1.lambda_handler"
    timeout = 30
    memory_size = 512
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"Function {function_name} exists, updating...")
            
            # Update function code
            with open("nutrition_coach_v2_1.zip", "rb") as f:
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
            with open("nutrition_coach_v2_1.zip", "rb") as f:
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

def main():
    """Main deployment process"""
    print("🚀 Starting NutritionGPT Coach v2.1 Deployment")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {missing_vars}")
        print("Please set these before running the deployment.")
        return False
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Step 2: Create deployment package
    if not create_deployment_package():
        print("❌ Failed to create deployment package")
        return False
    
    # Step 3: Deploy to Lambda
    if not deploy_to_lambda():
        print("❌ Failed to deploy to Lambda")
        return False
    
    print("✅ Deployment completed successfully!")
    print("\n🎉 NutritionGPT Coach v2.1 is now live!")
    print("\nKey Improvements:")
    print("- Enhanced vector-based memory with ChromaDB")
    print("- More human-like, conversational responses")
    print("- Better context awareness and personalization")
    print("- Improved user profile management")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 