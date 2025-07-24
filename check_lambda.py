#!/usr/bin/env python3
"""
Lambda Function Diagnostic Tool
This script checks your Lambda function status, logs, and configuration
"""

import boto3
import json
import requests
from datetime import datetime, timedelta

def check_lambda_function():
    """Check Lambda function status and configuration"""
    print("🔍 Checking Lambda function status...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Get function configuration
        response = lambda_client.get_function(FunctionName='NutritionGPTBot-v2')
        
        print("✅ Lambda function found!")
        print(f"📦 Function ARN: {response['Configuration']['FunctionArn']}")
        print(f"⏱️  Timeout: {response['Configuration']['Timeout']} seconds")
        print(f"💾 Memory: {response['Configuration']['MemorySize']} MB")
        print(f"🔄 Runtime: {response['Configuration']['Runtime']}")
        print(f"📅 Last modified: {response['Configuration']['LastModified']}")
        
        # Check environment variables
        env_vars = response['Configuration'].get('Environment', {}).get('Variables', {})
        print(f"\n🔧 Environment Variables:")
        if env_vars:
            for key, value in env_vars.items():
                # Mask sensitive values
                if 'token' in key.lower() or 'key' in key.lower():
                    masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  ❌ No environment variables found!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking Lambda function: {str(e)}")
        return False

def check_cloudwatch_logs():
    """Check recent CloudWatch logs"""
    print("\n📋 Checking recent CloudWatch logs...")
    
    try:
        logs_client = boto3.client('logs', region_name='eu-north-1')
        
        # Get log groups
        log_group_name = '/aws/lambda/NutritionGPTBot-v2'
        
        # Get recent log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if response['logStreams']:
            print(f"✅ Found {len(response['logStreams'])} recent log streams")
            
            for stream in response['logStreams'][:3]:  # Check last 3 streams
                print(f"\n📄 Log Stream: {stream['logStreamName']}")
                print(f"   Last Event: {stream.get('lastEventTimestamp', 'N/A')}")
                
                # Get log events
                try:
                    events_response = logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        startFromHead=False,
                        limit=10
                    )
                    
                    if events_response['events']:
                        print("   Recent events:")
                        for event in events_response['events'][-5:]:  # Last 5 events
                            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
                            message = event['message'][:100] + '...' if len(event['message']) > 100 else event['message']
                            print(f"     [{timestamp}] {message}")
                    else:
                        print("   No recent events")
                        
                except Exception as e:
                    print(f"   Error reading events: {str(e)}")
        else:
            print("❌ No log streams found")
            
    except Exception as e:
        print(f"❌ Error checking CloudWatch logs: {str(e)}")

def check_api_gateway():
    """Check API Gateway status"""
    print("\n🌐 Checking API Gateway...")
    
    try:
        apigateway = boto3.client('apigateway', region_name='eu-north-1')
        
        # List APIs
        response = apigateway.get_rest_apis()
        
        nutrition_api = None
        for api in response['items']:
            if 'NutritionGPTBot' in api['name']:
                nutrition_api = api
                break
        
        if nutrition_api:
            print(f"✅ Found API: {nutrition_api['name']}")
            print(f"   ID: {nutrition_api['id']}")
            print(f"   Created: {nutrition_api['createdDate']}")
            
            # Get stages
            stages_response = apigateway.get_stages(restApiId=nutrition_api['id'])
            if stages_response['item']:
                for stage in stages_response['item']:
                    print(f"   Stage: {stage['stageName']}")
                    print(f"   URL: https://{nutrition_api['id']}.execute-api.eu-north-1.amazonaws.com/{stage['stageName']}")
            else:
                print("   ❌ No stages found")
        else:
            print("❌ No NutritionGPTBot API found")
            
    except Exception as e:
        print(f"❌ Error checking API Gateway: {str(e)}")

def test_webhook_endpoint():
    """Test the webhook endpoint directly"""
    print("\n🧪 Testing webhook endpoint...")
    
    try:
        # Get API Gateway info first
        apigateway = boto3.client('apigateway', region_name='eu-north-1')
        response = apigateway.get_rest_apis()
        
        nutrition_api = None
        for api in response['items']:
            if 'NutritionGPTBot' in api['name']:
                nutrition_api = api
                break
        
        if nutrition_api:
            # Test webhook URL
            webhook_url = f"https://{nutrition_api['id']}.execute-api.eu-north-1.amazonaws.com/prod/webhook"
            
            # Sample test payload
            test_payload = {
                "test": "message",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"🔗 Testing URL: {webhook_url}")
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            print(f"📝 Response Body: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ Webhook endpoint is accessible")
            else:
                print(f"❌ Webhook endpoint returned error: {response.status_code}")
                
        else:
            print("❌ Could not find API Gateway to test")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")

def main():
    """Main diagnostic function"""
    print("🔧 Lambda Function Diagnostic Tool")
    print("=" * 50)
    
    # Check Lambda function
    if check_lambda_function():
        # Check CloudWatch logs
        check_cloudwatch_logs()
        
        # Check API Gateway
        check_api_gateway()
        
        # Test webhook endpoint
        test_webhook_endpoint()
        
        print("\n📋 Summary:")
        print("1. Check environment variables are set correctly")
        print("2. Look for errors in CloudWatch logs")
        print("3. Verify API Gateway is deployed")
        print("4. Test with real Telegram webhook")
    else:
        print("❌ Could not access Lambda function")

if __name__ == "__main__":
    main() 