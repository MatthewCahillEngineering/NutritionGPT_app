# Manual AWS Lambda Deployment Guide

## Prerequisites
- AWS CLI configured with your credentials
- Python 3.8+ installed
- Your Lambda function already created in AWS Console

## Step 1: Create Deployment Package

### Option A: Using the automated script
```bash
python deploy_to_aws.py
```

### Option B: Manual steps
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt -t lambda_package --upgrade
   ```

2. **Copy Lambda function:**
   ```bash
   copy lambda_function_v2.py lambda_package\lambda_function.py
   ```

3. **Create ZIP file:**
   - Select all files in `lambda_package` folder
   - Right-click → "Send to" → "Compressed (zipped) folder"
   - Name it `nutrition-bot-lambda.zip`

## Step 2: Upload to AWS Lambda

1. Go to AWS Lambda Console
2. Select your function
3. Go to "Code" tab
4. Click "Upload from" → ".zip file"
5. Upload your `nutrition-bot-lambda.zip`

## Step 3: Configure Environment Variables

1. In Lambda console, go to "Configuration" → "Environment variables"
2. Add these variables:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `OPENAI_API_KEY` = your OpenAI API key

## Step 4: Configure Runtime Settings

1. Go to "Configuration" → "General configuration"
2. Set:
   - **Handler:** `lambda_function.lambda_handler`
   - **Timeout:** 30 seconds
   - **Memory:** 512 MB (recommended)

## Step 5: Set up API Gateway

### Option A: Using the automated script
The script will create this automatically.

### Option B: Manual setup
1. Go to API Gateway Console
2. Create new REST API
3. Create a new resource called "webhook"
4. Create a POST method
5. Set integration type to "Lambda Function"
6. Select your Lambda function
7. Deploy the API to "prod" stage

## Step 6: Set Telegram Webhook

1. Get your API Gateway URL (format: `https://[api-id].execute-api.[region].amazonaws.com/prod/webhook`)
2. Set the webhook using this URL:
   ```
   https://api.telegram.org/bot[YOUR_BOT_TOKEN]/setWebhook?url=[YOUR_API_GATEWAY_URL]
   ```

## Step 7: Test Your Bot

1. Send a message to your bot
2. Check CloudWatch logs for any errors
3. Verify the bot responds correctly

## Troubleshooting

### Common Issues:

1. **Timeout errors:**
   - Increase Lambda timeout to 30 seconds
   - Check if OpenAI API calls are taking too long

2. **Permission errors:**
   - Ensure API Gateway has permission to invoke Lambda
   - Check IAM roles and policies

3. **Environment variable errors:**
   - Verify API keys are correct
   - Check variable names match exactly

4. **Webhook not receiving messages:**
   - Verify webhook URL is correct
   - Check API Gateway deployment
   - Ensure Lambda function is responding with 200 status

### Useful Commands:

```bash
# Check webhook status
curl "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getWebhookInfo"

# Delete webhook (if needed)
curl "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/deleteWebhook"

# Test Lambda function locally
python -c "import lambda_function; print(lambda_function.lambda_handler({'body': 'test'}, None))"
```

## Cost Optimization

- Lambda: Pay per request (very cheap for low usage)
- API Gateway: $3.50 per million requests
- CloudWatch: First 5GB free, then $0.50 per GB

For a typical bot with 1000 messages/day, costs should be under $1/month. 