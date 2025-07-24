"""
Quick setup script for NutritionGPT v2.0 webhook
"""

import requests
import json

def setup_webhook():
    """Setup webhook for v2.0 bot"""
    
    print("🚀 Setting up NutritionGPT v2.0 Webhook")
    print("=" * 50)
    
    # Get bot token
    bot_token = input("Enter your new bot token: ").strip()
    
    # Get webhook URL
    webhook_url = input("Enter your API Gateway webhook URL: ").strip()
    
    if not webhook_url.endswith('/webhook'):
        webhook_url = webhook_url.rstrip('/') + '/webhook'
    
    # Set webhook
    set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
    
    print(f"\n📡 Setting webhook to: {webhook_url}")
    
    try:
        response = requests.get(set_webhook_url)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"📊 Result: {result}")
        else:
            print("❌ Failed to set webhook")
            print(f"📊 Error: {result}")
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
    
    # Test webhook
    print(f"\n🧪 Testing webhook...")
    test_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(test_url)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result.get('result', {})
            print("✅ Webhook info retrieved:")
            print(f"   URL: {webhook_info.get('url', 'Not set')}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error: {webhook_info.get('last_error_message', 'None')}")
        else:
            print("❌ Failed to get webhook info")
            print(f"📊 Error: {result}")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def get_webhook_info():
    """Get current webhook info"""
    
    print("📊 Getting webhook info")
    print("=" * 30)
    
    bot_token = input("Enter your bot token: ").strip()
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result.get('result', {})
            print("✅ Webhook info:")
            print(f"   URL: {webhook_info.get('url', 'Not set')}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error: {webhook_info.get('last_error_message', 'None')}")
            print(f"   Max connections: {webhook_info.get('max_connections', 'Default')}")
        else:
            print("❌ Failed to get webhook info")
            print(f"📊 Error: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def delete_webhook():
    """Delete webhook"""
    
    print("🗑️ Deleting webhook")
    print("=" * 20)
    
    bot_token = input("Enter your bot token: ").strip()
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
        else:
            print("❌ Failed to delete webhook")
            print(f"📊 Error: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 NutritionGPT v2.0 Webhook Setup")
    print("=" * 40)
    print("1. Setup webhook")
    print("2. Get webhook info")
    print("3. Delete webhook")
    print("4. Exit")
    
    choice = input("\nChoose an option (1-4): ").strip()
    
    if choice == "1":
        setup_webhook()
    elif choice == "2":
        get_webhook_info()
    elif choice == "3":
        delete_webhook()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice") 