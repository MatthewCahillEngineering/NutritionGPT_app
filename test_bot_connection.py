#!/usr/bin/env python3
import requests
import json

def test_bot_connection():
    print("🤖 Testing Bot Connection...")
    
    token = "8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc"
    
    try:
        # Test bot info
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                print(f"✅ Bot is active: @{bot_info['result']['username']}")
                print(f"   Name: {bot_info['result']['first_name']}")
                print(f"   ID: {bot_info['result']['id']}")
                return True
            else:
                print(f"❌ Bot error: {bot_info}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_bot_connection() 