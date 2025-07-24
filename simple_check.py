#!/usr/bin/env python3
"""
Simple Lambda Check Tool
This script checks CloudWatch logs and helps verify webhook setup
"""

import boto3
import json
from datetime import datetime

def check_lambda_logs():
    """Check CloudWatch logs for Lambda function"""
    print("📋 Checking CloudWatch logs...")
    
    try:
        logs_client = boto3.client('logs', region_name='eu-north-1')
        
        # Get log groups
        log_group_name = '/aws/lambda/NutritionGPTBot-v2'
        
        # Get recent log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=3
        )
        
        if response['logStreams']:
            print(f"✅ Found {len(response['logStreams'])} recent log streams")
            
            for stream in response['logStreams']:
                print(f"\n📄 Log Stream: {stream['logStreamName']}")
                
                # Get log events
                try:
                    events_response = logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        startFromHead=False,
                        limit=5
                    )
                    
                    if events_response['events']:
                        print("   Recent events:")
                        for event in events_response['events']:
                            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
                            message = event['message']
                            print(f"     [{timestamp}] {message}")
                    else:
                        print("   No recent events")
                        
                except Exception as e:
                    print(f"   Error reading events: {str(e)}")
        else:
            print("❌ No log streams found")
            print("   This might mean the function hasn't been invoked yet")
            
    except Exception as e:
        print(f"❌ Error checking CloudWatch logs: {str(e)}")

def check_webhook_manually():
    """Provide manual webhook checking instructions"""
    print("\n🔍 Manual Webhook Check Instructions:")
    print("=" * 50)
    
    print("1. Go to AWS API Gateway Console:")
    print("   https://console.aws.amazon.com/apigateway/")
    print("   (Make sure you're in eu-north-1 region)")
    
    print("\n2. Look for your API:")
    print("   - Should be named 'NutritionGPTBot-API'")
    print("   - Click on it to see details")
    
    print("\n3. Check the stages:")
    print("   - Look for 'prod' stage")
    print("   - Copy the Invoke URL")
    print("   - Your webhook URL should be: [Invoke URL]/webhook")
    
    print("\n4. Test the webhook URL:")
    print("   - Open the webhook URL in browser")
    print("   - Should show some response (even if error)")
    
    print("\n5. Check Telegram webhook:")
    print("   - Visit: https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getWebhookInfo")
    print("   - Replace [YOUR_BOT_TOKEN] with your actual token")
    print("   - Should show the webhook URL and status")

def test_telegram_webhook():
    """Test Telegram webhook status"""
    print("\n📱 Testing Telegram webhook...")
    
    bot_token = input("Enter your bot token: ").strip()
    
    if not bot_token:
        print("❌ Bot token required")
        return
    
    try:
        import requests
        
        # Test getMe first
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                print(f"✅ Bot found: {bot_info.get('first_name')} (@{bot_info.get('username')})")
                
                # Check webhook info
                webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
                webhook_response = requests.get(webhook_url)
                
                if webhook_response.status_code == 200:
                    webhook_result = webhook_response.json()
                    if webhook_result.get('ok'):
                        webhook_info = webhook_result.get('result', {})
                        print(f"🔗 Webhook URL: {webhook_info.get('url', 'Not set')}")
                        print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
                        print(f"❌ Last error: {webhook_info.get('last_error_message', 'None')}")
                        
                        if webhook_info.get('url'):
                            print("✅ Webhook is set!")
                        else:
                            print("❌ No webhook URL found")
                    else:
                        print(f"❌ Failed to get webhook info: {webhook_result}")
                else:
                    print(f"❌ HTTP error: {webhook_response.status_code}")
            else:
                print(f"❌ Bot API error: {result}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Telegram: {str(e)}")

def main():
    """Main function"""
    print("🔧 Simple Lambda Check Tool")
    print("=" * 50)
    
    # Check logs
    check_lambda_logs()
    
    # Provide manual instructions
    check_webhook_manually()
    
    # Test Telegram webhook
    test_telegram_webhook()
    
    print("\n📋 Next Steps:")
    print("1. Check CloudWatch logs for any errors")
    print("2. Verify webhook URL is set correctly in Telegram")
    print("3. Test sending a message to your bot")
    print("4. Check logs again after sending a message")

if __name__ == "__main__":
    main() 