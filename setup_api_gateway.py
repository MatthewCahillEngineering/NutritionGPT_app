#!/usr/bin/env python3
"""
Setup API Gateway for Lambda function
"""
import boto3
import json

def setup_api_gateway():
    """Setup API Gateway for Lambda function"""
    print("🚀 Setting up API Gateway...")
    
    # Create API Gateway client
    apigateway = boto3.client('apigateway')
    lambda_client = boto3.client('lambda')
    
    try:
        # Create REST API
        print("Creating REST API...")
        api_response = apigateway.create_rest_api(
            name='NutritionGPTBot-API',
            description='API Gateway for NutritionGPT Telegram Bot'
        )
        api_id = api_response['id']
        print(f"✅ Created API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create resource for webhook
        print("Creating webhook resource...")
        resource_response = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='webhook'
        )
        resource_id = resource_response['id']
        print(f"✅ Created resource: {resource_id}")
        
        # Create POST method
        print("Creating POST method...")
        method_response = apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        print("✅ Created POST method")
        
        # Set up Lambda integration
        print("Setting up Lambda integration...")
        integration_response = apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:660753259090:function:NutritionGPTBot/invocations'
        )
        print("✅ Set up Lambda integration")
        
        # Add permission for API Gateway to invoke Lambda
        print("Adding Lambda permission...")
        lambda_client.add_permission(
            FunctionName='NutritionGPTBot',
            StatementId='apigateway',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:us-east-1:660753259090:{api_id}/*/*'
        )
        print("✅ Added Lambda permission")
        
        # Deploy API
        print("Deploying API...")
        deployment_response = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        print("✅ Deployed API")
        
        # Get the webhook URL
        webhook_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/webhook'
        print(f"🎉 Webhook URL: {webhook_url}")
        
        return webhook_url
        
    except Exception as e:
        print(f"❌ Error setting up API Gateway: {e}")
        return None

if __name__ == "__main__":
    webhook_url = setup_api_gateway()
    if webhook_url:
        print(f"\n📋 Next steps:")
        print(f"1. Set Telegram webhook: https://api.telegram.org/bot[YOUR_BOT_TOKEN]/setWebhook?url={webhook_url}")
        print(f"2. Test the webhook with a POST request to {webhook_url}")
    else:
        print("❌ Failed to setup API Gateway") 