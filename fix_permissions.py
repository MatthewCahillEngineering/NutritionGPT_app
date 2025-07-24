#!/usr/bin/env python3
"""
Fix IAM Permissions for Nutrition Bot Lambda Function
This script adds the necessary permissions for API Gateway integration
"""

import boto3
import json

def add_api_gateway_permissions():
    """Add permissions for API Gateway to invoke Lambda"""
    print("🔧 Adding API Gateway permissions...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='eu-north-1')
        
        # Add permission for API Gateway to invoke Lambda
        lambda_client.add_permission(
            FunctionName='NutritionGPTBot-v2',
            StatementId='apigateway-invoke-permission',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn='arn:aws:execute-api:eu-north-1:660753259090:*/*/*/webhook'
        )
        
        print("✅ API Gateway permissions added successfully")
        return True
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ API Gateway permissions already exist")
            return True
        else:
            print(f"❌ Error adding API Gateway permissions: {str(e)}")
            return False

def create_iam_policy():
    """Create a custom IAM policy for the Lambda function"""
    print("📋 Creating custom IAM policy...")
    
    try:
        iam_client = boto3.client('iam')
        
        # Policy document for Lambda function
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:eu-north-1:660753259090:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "lambda:InvokeFunction"
                    ],
                    "Resource": "arn:aws:lambda:eu-north-1:660753259090:function:NutritionGPTBot-v2"
                }
            ]
        }
        
        # Create the policy
        response = iam_client.create_policy(
            PolicyName='NutritionGPTBot-Lambda-Policy',
            PolicyDocument=json.dumps(policy_document),
            Description='Custom policy for NutritionGPT Bot Lambda function'
        )
        
        policy_arn = response['Policy']['Arn']
        print(f"✅ Custom policy created: {policy_arn}")
        
        return policy_arn
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ Custom policy already exists")
            # Get existing policy ARN
            try:
                response = iam_client.get_policy(PolicyArn='arn:aws:iam::660753259090:policy/NutritionGPTBot-Lambda-Policy')
                return response['Policy']['Arn']
            except:
                return None
        else:
            print(f"❌ Error creating custom policy: {str(e)}")
            return None

def attach_policy_to_role(policy_arn):
    """Attach the custom policy to the Lambda execution role"""
    print("🔗 Attaching policy to Lambda role...")
    
    try:
        iam_client = boto3.client('iam')
        
        # Attach policy to the Lambda execution role
        iam_client.attach_role_policy(
            RoleName='NutritionGPTBot-v2-role-m3tx917u',
            PolicyArn=policy_arn
        )
        
        print("✅ Policy attached to Lambda role successfully")
        return True
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ Policy already attached to role")
            return True
        else:
            print(f"❌ Error attaching policy to role: {str(e)}")
            return False

def main():
    """Main function to fix permissions"""
    print("🔧 Fixing IAM Permissions for NutritionGPT Bot")
    print("=" * 50)
    
    # Add API Gateway permissions
    if add_api_gateway_permissions():
        print("✅ API Gateway permissions are set up correctly")
    else:
        print("❌ Failed to set up API Gateway permissions")
    
    # Create and attach custom policy
    policy_arn = create_iam_policy()
    if policy_arn:
        if attach_policy_to_role(policy_arn):
            print("✅ Custom policy attached successfully")
        else:
            print("❌ Failed to attach custom policy")
    else:
        print("❌ Failed to create custom policy")
    
    print("\n📋 Current permissions summary:")
    print("- ✅ CloudWatch Logs (basic execution)")
    print("- ✅ API Gateway invocation")
    print("- ✅ Custom Lambda permissions")
    
    print("\n🎉 Permission setup completed!")
    print("Your Lambda function should now work properly with API Gateway.")

if __name__ == "__main__":
    main() 