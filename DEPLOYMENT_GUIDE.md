# 🚀 AWS Lambda Deployment Guide

This guide will walk you through deploying your NutritionGPT bot to AWS Lambda for production use.

## 📋 Prerequisites

1. **AWS Account**: You need an AWS account with billing enabled
2. **AWS CLI**: Install AWS CLI for easier deployment
3. **Python 3.12+**: For running deployment scripts
4. **Environment Variables**: Your bot token and OpenAI API key

## 🔧 Step 1: AWS Setup

### Install AWS CLI
```bash
# Windows (using pip)
pip install awscli

# Or download from: https://aws.amazon.com/cli/
```

### Configure AWS Credentials
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., `us-east-1`)
- Default output format (`json`)

### Create IAM User (Alternative)
If you don't have AWS CLI, create an IAM user:
1. Go to AWS Console → IAM → Users
2. Create new user
3. Attach policies: `AWSLambdaFullAccess`, `IAMFullAccess`
4. Create access keys

## 🔐 Step 2: Setup AWS Infrastructure

Run the AWS setup script to create required IAM roles:

```bash
python aws_setup.py
```

This will:
- ✅ Check your AWS credentials
- ✅ Create IAM role for Lambda execution
- ✅ Update deployment script with your account ID

## 🚀 Step 3: Deploy to Lambda

### Option A: Automated Deployment
```bash
python deploy.py
```

### Option B: Manual Deployment
If automated deployment fails, follow these steps:

1. **Create deployment package**:
```bash
python deploy.py
# This creates nutritiongpt-lambda.zip
```

2. **Upload to Lambda**:
```bash
aws lambda create-function \
  --function-name NutritionGPTBot \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/NutritionGPT-Lambda-Role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://nutritiongpt-lambda.zip \
  --timeout 30 \
  --memory-size 512
```

3. **Set environment variables**:
```bash
aws lambda update-function-configuration \
  --function-name NutritionGPTBot \
  --environment Variables='{TELEGRAM_BOT_TOKEN=your_bot_token,OPENAI_API_KEY=your_openai_key}'
```

4. **Create function URL**:
```bash
aws lambda create-function-url-config \
  --function-name NutritionGPTBot \
  --auth-type NONE
```

5. **Set Telegram webhook**:
```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url":"YOUR_FUNCTION_URL","allowed_updates":["message","callback_query"]}'
```

## 🔍 Step 4: Verify Deployment

### Check Lambda Function
1. Go to AWS Console → Lambda
2. Find your `NutritionGPTBot` function
3. Check the function URL in the "Configuration" tab

### Test the Bot
1. Send `/start` to @NutritionGPTAI_bot on Telegram
2. Try voice commands: "plan meals"
3. Test meal planning: `/planmeals`

### Monitor Logs
```bash
aws logs tail /aws/lambda/NutritionGPTBot --follow
```

## 🛠️ Troubleshooting

### Common Issues

**1. Permission Denied**
```bash
# Check IAM role permissions
aws iam get-role --role-name NutritionGPT-Lambda-Role
```

**2. Function Timeout**
- Increase timeout in Lambda configuration
- Check OpenAI API response times

**3. Memory Issues**
- Increase memory allocation (512MB recommended)
- Check for memory leaks in code

**4. Webhook Not Working**
```bash
# Check webhook status
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

### Debug Mode
Enable detailed logging in `lambda_function.py`:
```python
logger.setLevel(logging.DEBUG)
```

## 💰 Cost Optimization

### Lambda Pricing
- **Free tier**: 1M requests/month, 400K GB-seconds
- **Pay per use**: $0.20 per 1M requests + compute time

### Cost Reduction Tips
1. **Optimize memory**: Use minimum required memory
2. **Reduce timeout**: Set appropriate timeout values
3. **Cache responses**: Store frequently used data
4. **Batch processing**: Process multiple requests together

## 🔄 Updates & Maintenance

### Update Function Code
```bash
python deploy.py
```

### Update Environment Variables
```bash
aws lambda update-function-configuration \
  --function-name NutritionGPTBot \
  --environment Variables='{TELEGRAM_BOT_TOKEN=new_token,OPENAI_API_KEY=new_key}'
```

### Monitor Performance
- Check CloudWatch metrics
- Monitor error rates
- Track response times

## 🚨 Security Best Practices

1. **Environment Variables**: Never commit API keys to code
2. **IAM Roles**: Use least privilege principle
3. **VPC**: Consider using VPC for additional security
4. **Encryption**: Enable encryption at rest and in transit
5. **Monitoring**: Set up CloudWatch alarms

## 📞 Support

If you encounter issues:
1. Check AWS Lambda logs
2. Verify environment variables
3. Test locally first
4. Check Telegram bot token validity

## 🎉 Success!

Once deployed, your bot will be:
- ✅ Running 24/7 on AWS Lambda
- ✅ Scalable to handle multiple users
- ✅ Cost-effective (pay per use)
- ✅ Production-ready

Your NutritionGPT bot is now live and ready to help users with their nutrition planning! 🎊 