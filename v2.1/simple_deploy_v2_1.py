#!/usr/bin/env python3
"""
Simple deployment: Copy v2.1 code to v2.0 structure and deploy
"""

import os
import shutil
import subprocess
import sys

def copy_v2_1_to_v2_0():
    """Copy v2.1 code to v2.0 structure"""
    print("📋 Copying v2.1 code to v2.0 structure...")
    
    # Copy the main file
    shutil.copy("nutrition_coach_v2_1.py", "../v2.0/nutrition_coach_simple.py")
    print("✅ Copied nutrition_coach_v2_1.py to v2.0/nutrition_coach_simple.py")
    
    # Copy requirements
    shutil.copy("requirements.txt", "../v2.0/requirements_simple_v2.txt")
    print("✅ Copied requirements.txt to v2.0/requirements_simple_v2.txt")
    
    return True

def deploy_using_v2_0_script():
    """Use the existing v2.0 deployment script"""
    print("🚀 Using v2.0 deployment script...")
    
    # Change to v2.0 directory
    os.chdir("../v2.0")
    
    # Run the existing deployment script
    result = subprocess.run(["python", "deploy_to_v3.py"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Deployment successful!")
        print(result.stdout)
        return True
    else:
        print("❌ Deployment failed!")
        print(result.stderr)
        return False

def main():
    """Main deployment process"""
    print("🚀 Simple v2.1 Deployment")
    print("=" * 30)
    
    # Step 1: Copy files
    if not copy_v2_1_to_v2_0():
        return False
    
    # Step 2: Deploy using existing script
    if not deploy_using_v2_0_script():
        return False
    
    print("\n🎉 v2.1 successfully deployed to NutritionGPTBot-v3!")
    print("🌐 Webhook URL: https://rmdbpdtcll.execute-api.eu-north-1.amazonaws.com/prod/webhook")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 