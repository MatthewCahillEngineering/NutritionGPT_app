#!/usr/bin/env python3
"""
Quick Check - Lambda Function Status
"""

import boto3
import requests
import json
from datetime import datetime

def check_latest_logs():
    """Check the most recent CloudWatch logs"""
    print("📋 Checking latest CloudWatch logs...")
    
    try:
        logs_client = boto3.client('logs', region_name='eu-north-1')
        
        # Get the most recent log stream
        response = logs_client.describe_log_streams(
            logGroupName='/aws/lambda/NutritionGPTBot-v2',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if response['logStreams']:
            stream = response['logStreams'][0]
            print(f"📄 Latest Log Stream: {stream['logStreamName']}")
            
            # Get recent events
            events_response = logs_client.get_log_events(
                logGroupName='/aws/lambda/NutritionGPTBot-v2',
                logStreamName=stream['logStreamName'],
                startFromHead=False,
                limit=10
            )
            
            if events_response['events']:
                print("   Recent events:")
                for event in events_response['events']:
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
                    message = event['message']
                    print(f"     [{timestamp}] {message}")
            else:
                print("   No recent events")
        else:
            print("❌ No log streams found")
            
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")

def test_lambda_now():
    """Test Lambda function right now"""
    print("\n🧪 Testing Lambda function...")
    
    # Sample Telegram update
    sample_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {"id": 123456789, "first_name": "Test"},
            "chat": {"id": 123456789, "type": "private"},
            "date": 1234567890,
            "text": "/start"
        }
    }
    
    webhook_url = "https://z0t1c04qm7.execute-api.eu-north-1.amazonaws.com/prod/webhook"
    
    try:
        response = requests.post(webhook_url, json=sample_update, timeout=30)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Lambda responded successfully!")
        else:
            print(f"❌ Lambda error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🔧 Quick Lambda Check")
    print("=" * 30)
    
    # Check logs
    check_latest_logs()
    
    # Test function
    test_lambda_now()
    
    print("\n📋 Next steps:")
    print("1. Send a message to your bot")
    print("2. Check CloudWatch logs immediately")
    print("3. Look for any new errors")

if __name__ == "__main__":
    main() 