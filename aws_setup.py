#!/usr/bin/env python3
"""
AWS Infrastructure Setup for NutritionGPT Bot
Creates IAM roles, policies, and other required AWS resources
"""
import boto3
import json
import os
from botocore.exceptions import ClientError

def create_lambda_execution_role():
    """Create IAM role for Lambda execution"""
    print("🔐 Creating Lambda execution role...")
    
    iam = boto3.client('iam')
    role_name = 'NutritionGPT-Lambda-Role'
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permission policy for basic Lambda execution
    permission_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    try:
        # Check if role already exists
        try:
            response = iam.get_role(RoleName=role_name)
            print(f"✅ Role already exists: {role_name}")
            return response['Role']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                pass  # Role doesn't exist, create it
            else:
                raise e
        
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for NutritionGPT Lambda function'
        )
        
        # Attach permission policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='NutritionGPT-Policy',
            PolicyDocument=json.dumps(permission_policy)
        )
        
        # Attach basic Lambda execution role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ Created role: {role_name}")
        return response['Role']['Arn']
        
    except Exception as e:
        print(f"❌ Error creating role: {e}")
        return None

def setup_aws_credentials():
    """Guide user through AWS credentials setup"""
    print("🔑 AWS Credentials Setup")
    print("=" * 40)
    
    print("To deploy to AWS Lambda, you need to configure AWS credentials.")
    print("\nOption 1: AWS CLI (Recommended)")
    print("1. Install AWS CLI: https://aws.amazon.com/cli/")
    print("2. Run: aws configure")
    print("3. Enter your AWS Access Key ID, Secret Access Key, and region")
    
    print("\nOption 2: Environment Variables")
    print("Set these environment variables:")
    print("export AWS_ACCESS_KEY_ID=your_access_key")
    print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("export AWS_DEFAULT_REGION=us-east-1")
    
    print("\nOption 3: AWS IAM User Setup")
    print("1. Go to AWS Console → IAM → Users")
    print("2. Create a new user or use existing")
    print("3. Attach policies: AWSLambdaFullAccess, IAMFullAccess")
    print("4. Create access keys for the user")
    
    print("\n💡 For production, consider using AWS SSO or IAM roles for better security.")
    
    # Check if credentials are configured
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"\n✅ AWS credentials configured!")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"\n❌ AWS credentials not configured: {e}")
        return False

def get_account_id():
    """Get AWS account ID"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        return identity['Account']
    except Exception as e:
        print(f"❌ Error getting account ID: {e}")
        return None

def update_deploy_script():
    """Update deploy.py with correct account ID"""
    account_id = get_account_id()
    if not account_id:
        print("❌ Cannot update deploy script without account ID")
        return False
    
    print(f"📝 Updating deploy script with account ID: {account_id}")
    
    try:
        with open('deploy.py', 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual account ID
        content = content.replace(
            'arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role',
            f'arn:aws:iam::{account_id}:role/NutritionGPT-Lambda-Role'
        )
        
        with open('deploy.py', 'w') as f:
            f.write(content)
        
        print("✅ Deploy script updated!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating deploy script: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 NutritionGPT Bot - AWS Infrastructure Setup")
    print("=" * 50)
    
    # Check AWS credentials
    if not setup_aws_credentials():
        print("\n❌ Please configure AWS credentials first")
        return False
    
    # Create Lambda execution role
    role_arn = create_lambda_execution_role()
    if not role_arn:
        print("❌ Failed to create IAM role")
        return False
    
    # Update deploy script
    if update_deploy_script():
        print("\n✅ AWS infrastructure setup complete!")
        print("\n🚀 Next steps:")
        print("1. Run: python deploy.py")
        print("2. Your bot will be deployed to AWS Lambda")
        print("3. Test on Telegram: @NutritionGPTAI_bot")
        return True
    
    return False

if __name__ == "__main__":
    main() 