"""
Deploy NutritionGPT v2.0 to NutritionGPTBot-v3 Lambda function
"""

import os
import shutil
import zipfile
import boto3
import json
from pathlib import Path

def deploy_to_v3():
    """Deploy v2.0 to NutritionGPTBot-v3 function"""
    
    print("🚀 Deploying NutritionGPT v2.0 to NutritionGPTBot-v3")
    print("=" * 55)
    
    # Configuration from keys_v3
    FUNCTION_NAME = "NutritionGPTBot-v3"
    REGION = "eu-north-1"
    RUNTIME = "python3.12"
    HANDLER = "lambda_function.lambda_handler"
    TIMEOUT = 30
    MEMORY_SIZE = 256
    
    # Bot token from keys_v3
    BOT_TOKEN = "8220017583:AAHtGG443r3T4ql5_NcUbk28Po0Vce-kqqk"
    
    # OpenAI key from keys_v3
    OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
    
    print(f"📦 Creating deployment package for {FUNCTION_NAME}...")
    
    # Create deployment directory
    deployment_dir = "v3_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Copy main function (rename to lambda_function.py)
    shutil.copy("nutrition_coach_simple.py", f"{deployment_dir}/lambda_function.py")
    
    # Install dependencies (using simplified requirements)
    print("📚 Installing dependencies...")
    os.system(f"pip install -r requirements_simple_v2.txt -t {deployment_dir} --upgrade")
    
    # Create ZIP file
    zip_filename = "v3_deployment.zip"
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
        print(f"🔄 Updating function: {FUNCTION_NAME}")
        
        # Update function code
        with open(zip_filename, 'rb') as zip_file:
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
        print("\n📡 Webhook URL:")
        print("https://rmdbpdtcll.execute-api.eu-north-1.amazonaws.com/prod/webhook")
        print("\n🎯 Next: Set webhook using setup_v2_webhook.py")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_to_v3() 