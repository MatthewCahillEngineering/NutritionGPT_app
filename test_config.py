#!/usr/bin/env python3
from config import validate_config, TELEGRAM_TOKEN, OPENAI_API_KEY

def test_config():
    print("🔧 Testing Configuration...")
    
    try:
        # Test configuration validation
        validate_config()
        print("✅ Configuration validation passed")
        
        # Test API keys are loaded
        print(f"✅ Telegram Token: {TELEGRAM_TOKEN[:20]}...")
        print(f"✅ OpenAI API Key: {OPENAI_API_KEY[:20]}...")
        
        # Test AI service
        from ai_service import AIService
        ai = AIService()
        print("✅ AI Service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    test_config() 