"""
Deploy NutritionGPT Coach v2.0 - Conversational AI Nutrition Assistant
"""

import os
import shutil
import zipfile
import boto3
import json
from pathlib import Path

def deploy_conversational_coach():
    """Deploy the conversational nutrition coach to AWS Lambda"""
    
    # Configuration
    FUNCTION_NAME = "NutritionGPTBot-v2"
    REGION = "eu-north-1"
    RUNTIME = "python3.12"
    HANDLER = "nutrition_coach_simple.lambda_handler"
    TIMEOUT = 30
    MEMORY_SIZE = 256  # Increased for AI processing
    
    print("🚀 Deploying NutritionGPT Coach v2.0 - Conversational AI Assistant")
    print("=" * 60)
    
    # Create deployment directory
    deployment_dir = "conversational_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    print("📦 Creating deployment package...")
    
    # Copy main function
    shutil.copy("nutrition_coach_simple.py", f"{deployment_dir}/lambda_function.py")
    
    # Install dependencies
    print("📚 Installing dependencies...")
    os.system(f"pip install -r requirements_simple.txt -t {deployment_dir} --upgrade")
    
    # Create ZIP file
    zip_filename = "conversational_coach.zip"
    print(f"🗜️ Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"📏 Package size: {zip_size:.2f} MB")
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Update function code
        print(f"🔄 Updating Lambda function: {FUNCTION_NAME}")
        
        with open(zip_filename, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName=FUNCTION_NAME,
                ZipFile=zip_file.read()
            )
        
        # Update function configuration
        print("⚙️ Updating function configuration...")
        lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Runtime=RUNTIME,
            Handler=HANDLER,
            Timeout=TIMEOUT,
            MemorySize=MEMORY_SIZE,
            Environment={
                'Variables': {
                    'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
                    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')
                }
            }
        )
        
        print("✅ Deployment successful!")
        print("\n🎯 New Features Available:")
        print("• Conversational memory - remembers user preferences")
        print("• User profiles - stores goals and measurements")
        print("• Meal logging - tracks nutrition intake")
        print("• Personalized responses - context-aware AI")
        print("• Proactive coaching - smart reminders and check-ins")
        
        print(f"\n📊 Function Details:")
        print(f"• Name: {FUNCTION_NAME}")
        print(f"• Runtime: {RUNTIME}")
        print(f"• Memory: {MEMORY_SIZE} MB")
        print(f"• Timeout: {TIMEOUT} seconds")
        print(f"• Handler: {HANDLER}")
        
        # Clean up
        shutil.rmtree(deployment_dir)
        os.remove(zip_filename)
        
        print("\n🧹 Cleanup complete!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    return True

def test_conversational_features():
    """Test the conversational features locally"""
    print("\n🧪 Testing conversational features...")
    
    try:
        from nutrition_coach_simple import NutritionCoach
        
        # Initialize coach
        coach = NutritionCoach(openai_api_key="test-key")
        
        # Test conversation flow
        test_user = "test_user_123"
        
        print("Testing conversation flow...")
        
        # Test 1: Initial greeting
        response1 = coach.process_message(test_user, "Hi! I want to start tracking my nutrition and build muscle.")
        print(f"Response 1: {response1[:100]}...")
        
        # Test 2: Profile setup
        response2 = coach.process_message(test_user, "I'm 180 lbs, 6'0\", 25 years old")
        print(f"Response 2: {response2[:100]}...")
        
        # Test 3: Activity level
        response3 = coach.process_message(test_user, "I work out 4 times a week")
        print(f"Response 3: {response3[:100]}...")
        
        # Test 4: Meal logging
        response4 = coach.process_message(test_user, "I just ate grilled chicken with rice for lunch")
        print(f"Response 4: {response4[:100]}...")
        
        print("✅ Local testing completed!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")

def show_feature_comparison():
    """Show comparison between v1.0 and v2.0"""
    print("\n📊 Feature Comparison: v1.0 vs v2.0")
    print("=" * 50)
    
    comparison = {
        "Basic Meal Planning": {"v1": "✅", "v2": "✅"},
        "Telegram Integration": {"v1": "✅", "v2": "✅"},
        "AWS Lambda Deployment": {"v1": "✅", "v2": "✅"},
        "Conversation Memory": {"v1": "❌", "v2": "✅"},
        "User Profiles": {"v1": "❌", "v2": "✅"},
        "Meal Logging": {"v1": "❌", "v2": "✅"},
        "Personalized Responses": {"v1": "❌", "v2": "✅"},
        "Proactive Messaging": {"v1": "❌", "v2": "✅"},
        "Nutrition Knowledge Base": {"v1": "❌", "v2": "✅"},
        "Context-Aware AI": {"v1": "❌", "v2": "✅"}
    }
    
    print(f"{'Feature':<25} {'v1.0':<8} {'v2.0':<8}")
    print("-" * 50)
    
    for feature, versions in comparison.items():
        print(f"{feature:<25} {versions['v1']:<8} {versions['v2']:<8}")

if __name__ == "__main__":
    print("🎯 NutritionGPT Coach v2.0 Deployment")
    print("=" * 40)
    
    # Show feature comparison
    show_feature_comparison()
    
    # Test features locally
    test_conversational_features()
    
    # Deploy to AWS
    deploy = input("\n🚀 Deploy to AWS Lambda? (y/n): ").lower().strip()
    
    if deploy == 'y':
        success = deploy_conversational_coach()
        if success:
            print("\n🎉 NutritionGPT Coach v2.0 is now live!")
            print("Start chatting with your AI nutrition coach!")
        else:
            print("\n❌ Deployment failed. Check the logs above.")
    else:
        print("\n📝 Deployment skipped. You can run this script again later.") 