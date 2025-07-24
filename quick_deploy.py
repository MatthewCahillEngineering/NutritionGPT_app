#!/usr/bin/env python3
"""
Quick Deploy - Update Lambda Function
"""

import os
import shutil
import zipfile
import boto3
import subprocess

def quick_deploy():
    """Quickly deploy the updated Lambda function"""
    print("🚀 Quick Deploy - Updated Lambda Function")
    print("=" * 40)
    
    # Clean and create package
    if os.path.exists('lambda_package'):
        shutil.rmtree('lambda_package')
    os.makedirs('lambda_package', exist_ok=True)
    
    # Copy updated function
    shutil.copy('lambda_function_simple.py', 'lambda_package/lambda_function.py')
    
    # Install dependencies
    print("📥 Installing dependencies...")
    subprocess.run([
        'pip', 'install', '-r', 'requirements_simple.txt', 
        '-t', 'lambda_package', '--upgrade'
    ], check=True)
    
    # Create ZIP
    zip_filename = 'quick-update.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('lambda_package'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'lambda_package')
                zipf.write(file_path, arcname)
    
    # Upload to Lambda
    print("☁️ Uploading to Lambda...")
    lambda_client = boto3.client('lambda', region_name='eu-north-1')
    
    with open(zip_filename, 'rb') as zip_file:
        response = lambda_client.update_function_code(
            FunctionName='NutritionGPTBot-v2',
            ZipFile=zip_file.read()
        )
    
    print("✅ Lambda function updated!")
    print(f"📅 Last modified: {response['LastModified']}")
    
    # Clean up
    os.remove(zip_filename)
    shutil.rmtree('lambda_package')
    
    print("\n🎉 Quick deploy complete!")
    print("📱 Test your bot now with /start")

if __name__ == "__main__":
    quick_deploy() 