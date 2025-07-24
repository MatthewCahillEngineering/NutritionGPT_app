#!/usr/bin/env python3
"""
Deploy Simplified Lambda Function
This script creates a clean deployment package and uploads it
"""

import os
import shutil
import zipfile
import boto3
import subprocess

def create_deployment_package():
    """Create the deployment package with minimal dependencies"""
    print("📦 Creating simplified deployment package...")
    
    # Clean up existing package
    if os.path.exists('lambda_package'):
        shutil.rmtree('lambda_package')
    
    # Create fresh package directory
    os.makedirs('lambda_package', exist_ok=True)
    
    # Copy the simplified Lambda function
    shutil.copy('lambda_function_simple.py', 'lambda_package/lambda_function.py')
    
    # Install minimal dependencies
    print("📥 Installing minimal dependencies...")
    try:
        subprocess.run([
            'pip', 'install', '-r', 'requirements_simple.txt', 
            '-t', 'lambda_package', '--upgrade'
        ], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    # Create ZIP file
    print("🗜️ Creating ZIP file...")
    zip_filename = 'nutrition-bot-simple.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('lambda_package'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'lambda_package')
                zipf.write(file_path, arcname)
    
    print(f"✅ ZIP file created: {zip_filename}")
    return zip_filename

def upload_to_lambda(zip_filename):
    """Upload the ZIP file to Lambda"""
    print("☁️ Uploading to AWS Lambda...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Read the ZIP file
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the function code
        response = lambda_client.update_function_code(
            FunctionName='NutritionGPTBot-v2',
            ZipFile=zip_content
        )
        
        print("✅ Lambda function updated successfully!")
        print(f"📦 Function ARN: {response['FunctionArn']}")
        print(f"📅 Last modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to Lambda: {str(e)}")
        return False

def clean_up(zip_filename):
    """Clean up temporary files"""
    print("🧹 Cleaning up...")
    
    # Remove ZIP file
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f"🗑️ Removed {zip_filename}")
    
    # Remove package directory
    if os.path.exists('lambda_package'):
        shutil.rmtree('lambda_package')
        print("🗑️ Removed lambda_package directory")

def main():
    """Main deployment function"""
    print("🚀 Deploying Simplified NutritionGPT Bot")
    print("=" * 50)
    
    # Create deployment package
    zip_filename = create_deployment_package()
    if not zip_filename:
        print("❌ Failed to create deployment package")
        return
    
    # Upload to Lambda
    if upload_to_lambda(zip_filename):
        print("\n🎉 Deployment successful!")
        print("\n📋 Next steps:")
        print("1. Test your bot by sending /start")
        print("2. Check CloudWatch logs for any errors")
        print("3. Try /planmeals command")
    else:
        print("\n❌ Deployment failed")
    
    # Clean up
    clean_up(zip_filename)

if __name__ == "__main__":
    main() 