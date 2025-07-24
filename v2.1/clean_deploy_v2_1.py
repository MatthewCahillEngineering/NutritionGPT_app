#!/usr/bin/env python3
"""
Clean deployment script for v2.1 - no emojis, no local installs
"""

import os
import sys
import subprocess
import zipfile
import boto3
import tempfile
import shutil

def install_dependencies_to_temp():
    """Install dependencies to temporary directory"""
    print("Installing dependencies to temporary directory...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Using temp directory: {temp_dir}")
    
    # Install packages to temp directory
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
        cmd = f"pip install {package} -t {temp_dir}"
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error installing {package}: {result.stderr}")
            return None
    
    return temp_dir

def create_deployment_package(temp_dir):
    """Create the deployment package"""
    print("Creating deployment package...")
    
    # Files to include
    files_to_include = [
        "nutrition_coach_v2_1.py",
        "requirements.txt"
    ]
    
    # Create zip file
    with zipfile.ZipFile("v2_1_deployment.zip", "w") as zipf:
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
    
    print("Deployment package created: v2_1_deployment.zip")
    return True

def deploy_to_lambda():
    """Deploy to existing NutritionGPTBot-v3 Lambda function"""
    print("Deploying to existing NutritionGPTBot-v3 Lambda function...")
    
    # Configuration from keys_v3
    FUNCTION_NAME = "NutritionGPTBot-v3"
    REGION = "eu-north-1"
    RUNTIME = "python3.12"
    HANDLER = "nutrition_coach_v2_1.lambda_handler"
    TIMEOUT = 30
    MEMORY_SIZE = 512
    
    # Bot token from keys_v3
    BOT_TOKEN = "8220017583:AAHtGG443r3T4ql5_NcUbk28Po0Vce-kqqk"
    
    # OpenAI key from keys_v3
    OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        print(f"Updating function: {FUNCTION_NAME}")
        
        # Update function code
        with open("v2_1_deployment.zip", "rb") as zip_file:
            lambda_client.update_function_code(
                FunctionName=FUNCTION_NAME,
                ZipFile=zip_file.read()
            )
        
        # Wait a moment for code update to complete
        import time
        time.sleep(5)
        
        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Runtime=RUNTIME,
            Handler=HANDLER,
            Timeout=TIMEOUT,
            MemorySize=MEMORY_SIZE,
            Environment={
                'Variables': {
                    'TELEGRAM_BOT_TOKEN': BOT_TOKEN,
                    'OPENAI_API_KEY': OPENAI_KEY
                }
            }
        )
        
        print("Deployment successful!")
        print(f"Function Details:")
        print(f"Name: {FUNCTION_NAME}")
        print(f"Runtime: {RUNTIME}")
        print(f"Memory: {MEMORY_SIZE} MB")
        print(f"Timeout: {TIMEOUT} seconds")
        print(f"Handler: {HANDLER}")
        print(f"Webhook URL: https://rmdbpdtcll.execute-api.eu-north-1.amazonaws.com/prod/webhook")
        
        return True
        
    except Exception as e:
        print(f"Error deploying to Lambda: {e}")
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
    print("Starting NutritionGPT Coach v2.1 Deployment to v3 Lambda")
    print("=" * 60)
    
    temp_dir = None
    try:
        # Step 1: Install dependencies to temp directory
        temp_dir = install_dependencies_to_temp()
        if not temp_dir:
            print("Failed to install dependencies")
            return False
        
        # Step 2: Create deployment package
        if not create_deployment_package(temp_dir):
            print("Failed to create deployment package")
            return False
        
        # Step 3: Deploy to Lambda
        if not deploy_to_lambda():
            print("Failed to deploy to Lambda")
            return False
        
        print("Deployment completed successfully!")
        print("NutritionGPT Coach v2.1 is now live on NutritionGPTBot-v3!")
        print("Key Improvements:")
        print("- Enhanced vector-based memory with ChromaDB")
        print("- More human-like, conversational responses")
        print("- Better context awareness and personalization")
        print("- Improved user profile management")
        print("Webhook URL: https://rmdbpdtcll.execute-api.eu-north-1.amazonaws.com/prod/webhook")
        
        return True
        
    finally:
        # Always clean up temp directory
        cleanup_temp_dir(temp_dir)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 