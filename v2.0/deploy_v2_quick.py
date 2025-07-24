"""
Quick deployment script for NutritionGPT v2.0
"""

import os
import shutil
import zipfile
import boto3
import json
from pathlib import Path

def deploy_v2_quick():
    """Quick deploy v2.0 to new Lambda function"""
    
    print("🚀 Quick Deploy NutritionGPT v2.0")
    print("=" * 40)
    
    # Configuration
    FUNCTION_NAME = input("Enter new Lambda function name (e.g., NutritionGPT-v2): ").strip()
    REGION = "eu-north-1"
    RUNTIME = "python3.12"
    HANDLER = "nutrition_coach_simple.lambda_handler"
    TIMEOUT = 30
    MEMORY_SIZE = 256
    
    # Get bot token
    bot_token = input("Enter your new bot token: ").strip()
    
    # Get OpenAI key (reuse existing or enter new)
    openai_key = input("Enter OpenAI API key (or press Enter to use existing): ").strip()
    if not openai_key:
        # Try to get from environment
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai_key:
            openai_key = input("Please enter OpenAI API key: ").strip()
    
    print(f"\n📦 Creating deployment package for {FUNCTION_NAME}...")
    
    # Create deployment directory
    deployment_dir = "v2_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Copy main function
    shutil.copy("nutrition_coach_simple.py", f"{deployment_dir}/lambda_function.py")
    
    # Install dependencies
    print("📚 Installing dependencies...")
    os.system(f"pip install -r requirements_v2.txt -t {deployment_dir} --upgrade")
    
    # Create ZIP file
    zip_filename = "v2_deployment.zip"
    print(f"🗜️ Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"📏 Package size: {zip_size:.2f} MB")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=FUNCTION_NAME)
            print(f"🔄 Updating existing function: {FUNCTION_NAME}")
            
            # Update function code
            with open(zip_filename, 'rb') as zip_file:
                lambda_client.update_function_code(
                    FunctionName=FUNCTION_NAME,
                    ZipFile=zip_file.read()
                )
            
            # Update function configuration
            lambda_client.update_function_configuration(
                FunctionName=FUNCTION_NAME,
                Runtime=RUNTIME,
                Handler=HANDLER,
                Timeout=TIMEOUT,
                MemorySize=MEMORY_SIZE,
                Environment={
                    'Variables': {
                        'TELEGRAM_BOT_TOKEN': bot_token,
                        'OPENAI_API_KEY': openai_key
                    }
                }
            )
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"🆕 Creating new function: {FUNCTION_NAME}")
            
            # Create function
            with open(zip_filename, 'rb') as zip_file:
                lambda_client.create_function(
                    FunctionName=FUNCTION_NAME,
                    Runtime=RUNTIME,
                    Handler=HANDLER,
                    Code={'ZipFile': zip_file.read()},
                    Timeout=TIMEOUT,
                    MemorySize=MEMORY_SIZE,
                    Environment={
                        'Variables': {
                            'TELEGRAM_BOT_TOKEN': bot_token,
                            'OPENAI_API_KEY': openai_key
                        }
                    },
                    Role='arn:aws:iam::660753259090:role/lambda-role'  # Use your existing role
                )
        
        print("✅ Deployment successful!")
        print(f"\n🎯 Function Details:")
        print(f"• Name: {FUNCTION_NAME}")
        print(f"• Runtime: {RUNTIME}")
        print(f"• Memory: {MEMORY_SIZE} MB")
        print(f"• Timeout: {TIMEOUT} seconds")
        print(f"• Handler: {HANDLER}")
        
        # Clean up
        shutil.rmtree(deployment_dir)
        os.remove(zip_filename)
        
        print("\n🧹 Cleanup complete!")
        print("\n📡 Next steps:")
        print("1. Create API Gateway with /webhook endpoint")
        print("2. Set webhook URL using setup_v2_webhook.py")
        print("3. Test the bot!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_v2_quick() 