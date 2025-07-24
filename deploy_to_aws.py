#!/usr/bin/env python3
"""
AWS Lambda Deployment Script for Nutrition Bot
This script packages and deploys the bot to AWS Lambda
"""

import os
import shutil
import zipfile
import boto3
import json
from pathlib import Path

def create_deployment_package():
    """Create the deployment package with all dependencies"""
    print("📦 Creating deployment package...")
    
    # Clean up existing package
    if os.path.exists('lambda_package'):
        shutil.rmtree('lambda_package')
    
    # Create fresh package directory
    os.makedirs('lambda_package', exist_ok=True)
    
    # Copy the main Lambda function
    shutil.copy('lambda_function_v2.py', 'lambda_package/lambda_function.py')
    
    # Install dependencies
    print("📥 Installing dependencies...")
    os.system('pip install -r requirements.txt -t lambda_package --quiet')
    
    # Create ZIP file
    print("🗜️ Creating ZIP file...")
    with zipfile.ZipFile('nutrition-bot-lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('lambda_package'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'lambda_package')
                zipf.write(file_path, arcname)
    
    print("✅ Deployment package created: nutrition-bot-lambda.zip")
    return 'nutrition-bot-lambda.zip'

def deploy_to_lambda(function_name, zip_file):
    """Deploy the package to AWS Lambda"""
    print(f"🚀 Deploying to Lambda function: {function_name}")
    
    try:
        # Use the specific region from the ARN
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Read the ZIP file
        with open(zip_file, 'rb') as f:
            zip_content = f.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully deployed to {function_name}")
        print(f"📋 Function ARN: {response['FunctionArn']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to Lambda: {str(e)}")
        return False

def setup_environment_variables(function_name):
    """Set up environment variables for the Lambda function"""
    print("🔧 Setting up environment variables...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Get current configuration
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        current_env = response.get('Environment', {}).get('Variables', {})
        
        # Required environment variables
        required_vars = {
            'TELEGRAM_BOT_TOKEN': 'YOUR_TELEGRAM_BOT_TOKEN',
            'OPENAI_API_KEY': 'YOUR_OPENAI_API_KEY'
        }
        
        # Update environment variables
        updated_env = {**current_env, **required_vars}
        
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': updated_env}
        )
        
        print("✅ Environment variables configured")
        print("⚠️  Remember to update the actual values in AWS Console!")
        
    except Exception as e:
        print(f"❌ Error setting environment variables: {str(e)}")

def setup_api_gateway(function_name):
    """Set up API Gateway for the Lambda function"""
    print("🌐 Setting up API Gateway...")
    
    try:
        # Create API Gateway client in the same region
        apigateway = boto3.client('apigateway', region_name='eu-north-1')
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Create REST API
        api_response = apigateway.create_rest_api(
            name=f'{function_name}-api',
            description='API Gateway for Nutrition Bot'
        )
        
        api_id = api_response['id']
        root_id = apigateway.get_resources(restApiId=api_id)['items'][0]['id']
        
        # Create resource
        resource_response = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='webhook'
        )
        
        resource_id = resource_response['id']
        
        # Create POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Get Lambda function ARN
        lambda_arn = lambda_client.get_function(FunctionName=function_name)['Configuration']['FunctionArn']
        
        # Set up integration
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:eu-north-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
        )
        
        # Deploy API
        deployment_response = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        # Grant API Gateway permission to invoke Lambda
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='apigateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:eu-north-1:*:{api_id}/*/*/webhook'
        )
        
        webhook_url = f'https://{api_id}.execute-api.eu-north-1.amazonaws.com/prod/webhook'
        
        print(f"✅ API Gateway created successfully")
        print(f"🔗 Webhook URL: {webhook_url}")
        print(f"📝 Set this URL as your Telegram webhook")
        
        return webhook_url
        
    except Exception as e:
        print(f"❌ Error setting up API Gateway: {str(e)}")
        return None

def main():
    """Main deployment function"""
    print("🤖 Nutrition Bot AWS Lambda Deployment")
    print("=" * 50)
    
    # Use the function name from the ARN
    function_name = "NutritionGPTBot-v2"
    print(f"🎯 Target function: {function_name}")
    print(f"🌍 Region: eu-north-1")
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Deploy to Lambda
    if deploy_to_lambda(function_name, zip_file):
        # Set up environment variables
        setup_environment_variables(function_name)
        
        # Set up API Gateway
        webhook_url = setup_api_gateway(function_name)
        
        if webhook_url:
            print("\n🎉 Deployment completed successfully!")
            print("\n📋 Next steps:")
            print("1. Go to AWS Lambda Console (eu-north-1 region)")
            print("2. Update environment variables with your actual API keys:")
            print("   - TELEGRAM_BOT_TOKEN")
            print("   - OPENAI_API_KEY")
            print("3. Set the webhook URL in Telegram:")
            print(f"   {webhook_url}")
            print("4. Test your bot!")
        else:
            print("\n⚠️ Deployment completed but API Gateway setup failed")
            print("You may need to set up API Gateway manually")
    
    else:
        print("\n❌ Deployment failed")
    
    # Clean up
    if os.path.exists('nutrition-bot-lambda.zip'):
        os.remove('nutrition-bot-lambda.zip')
        print("🧹 Cleaned up temporary files")

if __name__ == "__main__":
    main() 