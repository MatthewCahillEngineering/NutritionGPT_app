#!/usr/bin/env python3
"""
Setup script for NutritionGPT Bot
Automates the initial setup process
"""

import os
import sys
import subprocess
import requests

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_openai_api_key():
    """Check if OpenAI API key is set"""
    print("🔑 Checking OpenAI API key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please get your API key from: https://platform.openai.com/api-keys")
        print("Then set it: export OPENAI_API_KEY=your_key_here")
        return False
    
    # Test the API key
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✅ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key test failed: {e}")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("☁️ Checking AWS credentials...")
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials configured for account: {identity['Account']}")
        return True
    except Exception as e:
        print("❌ AWS credentials not configured!")
        print("Please run: aws configure")
        return False

def test_telegram_bot():
    """Test Telegram bot connection"""
    print("🤖 Testing Telegram bot connection...")
    token = "8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc"
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                print(f"✅ Bot connection successful: @{bot_info['result']['username']}")
                return True
        print("❌ Bot connection failed")
        return False
    except Exception as e:
        print(f"❌ Bot connection error: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("📝 Creating environment file...")
    env_content = """# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# AWS Configuration (Optional - defaults provided)
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=nutrition_tracker

# Telegram Bot Token (Already configured in config.py)
# TELEGRAM_TOKEN=8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please update .env with your OpenAI API key")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 NutritionGPT Bot Setup\n")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("OpenAI API Key", check_openai_api_key),
        ("AWS Credentials", check_aws_credentials),
        ("Telegram Bot", test_telegram_bot),
        ("Environment File", create_env_file),
        ("Tests", run_tests)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        else:
            print(f"⚠️  {name} check failed - manual intervention may be required")
    
    print("\n" + "=" * 50)
    print(f"📊 Setup Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Test locally: python bot.py")
        print("2. Deploy to AWS: python deploy.py")
        print("3. Test your bot: t.me/NutritionGPTAI_bot")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("- Set OpenAI API key: export OPENAI_API_KEY=your_key")
        print("- Configure AWS: aws configure")
        print("- Install dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 