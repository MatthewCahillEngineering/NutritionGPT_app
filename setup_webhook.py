#!/usr/bin/env python3
"""
Setup API Gateway and Telegram Webhook for Nutrition Bot
This script creates the API Gateway and sets up the webhook
"""

import boto3
import requests
import json
import os

def create_api_gateway():
    """Create API Gateway for the Lambda function"""
    print("🌐 Creating API Gateway...")
    
    try:
        # Create API Gateway client
        apigateway = boto3.client('apigateway', region_name='eu-north-1')
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Create REST API
        api_response = apigateway.create_rest_api(
            name='NutritionGPTBot-API',
            description='API Gateway for NutritionGPT Bot'
        )
        
        api_id = api_response['id']
        print(f"✅ API Gateway created with ID: {api_id}")
        
        # Get root resource ID
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create webhook resource
        resource_response = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='webhook'
        )
        
        resource_id = resource_response['id']
        print(f"✅ Webhook resource created with ID: {resource_id}")
        
        # Create POST method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Get Lambda function ARN
        lambda_arn = lambda_client.get_function(FunctionName='NutritionGPTBot-v2')['Configuration']['FunctionArn']
        
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
        
        print("✅ API Gateway deployed to prod stage")
        
        # Grant API Gateway permission to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName='NutritionGPTBot-v2',
                StatementId='apigateway-invoke-permission',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:eu-north-1:660753259090:{api_id}/*/*/webhook'
            )
            print("✅ Lambda permissions granted")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"⚠️ Warning: {str(e)}")
        
        webhook_url = f'https://{api_id}.execute-api.eu-north-1.amazonaws.com/prod/webhook'
        print(f"✅ API Gateway setup complete!")
        print(f"🔗 Webhook URL: {webhook_url}")
        
        return webhook_url
        
    except Exception as e:
        print(f"❌ Error creating API Gateway: {str(e)}")
        return None

def set_telegram_webhook(webhook_url, bot_token):
    """Set the webhook URL in Telegram"""
    print("📱 Setting Telegram webhook...")
    
    try:
        # Set webhook URL
        webhook_set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
        response = requests.get(webhook_set_url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                print(f"📋 Webhook info: {result}")
                return True
            else:
                print(f"❌ Failed to set webhook: {result}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {str(e)}")
        return False

def test_webhook(bot_token):
    """Test the webhook configuration"""
    print("🧪 Testing webhook configuration...")
    
    try:
        # Get webhook info
        webhook_info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(webhook_info_url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                if webhook_info.get('url'):
                    print("✅ Webhook is active!")
                    print(f"🔗 URL: {webhook_info.get('url')}")
                    print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
                    return True
                else:
                    print("❌ No webhook URL found")
                    return False
            else:
                print(f"❌ Failed to get webhook info: {result}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🤖 Setting up API Gateway and Webhook")
    print("=" * 50)
    
    # Get bot token from user
    bot_token = input("Enter your Telegram bot token: ").strip()
    
    if not bot_token:
        print("❌ Bot token is required")
        return
    
    # Create API Gateway
    webhook_url = create_api_gateway()
    
    if webhook_url:
        # Set Telegram webhook
        if set_telegram_webhook(webhook_url, bot_token):
            print("\n🎉 Webhook setup completed successfully!")
            
            # Test the webhook
            if test_webhook(bot_token):
                print("\n✅ Everything is working!")
                print("\n📋 Next steps:")
                print("1. Make sure environment variables are set in Lambda:")
                print("   - TELEGRAM_BOT_TOKEN")
                print("   - OPENAI_API_KEY")
                print("2. Test your bot by sending a message!")
            else:
                print("\n⚠️ Webhook setup completed but test failed")
                print("Check your bot token and try again")
        else:
            print("\n❌ Failed to set webhook")
    else:
        print("\n❌ Failed to create API Gateway")

if __name__ == "__main__":
    main() 