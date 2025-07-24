# Manual API Gateway Setup Guide

Since your AWS user doesn't have API Gateway permissions, follow these manual steps:

## Step 1: Create API Gateway (Manual)

1. **Go to AWS API Gateway Console**
   - Navigate to: https://console.aws.amazon.com/apigateway/
   - Make sure you're in the `eu-north-1` region

2. **Create REST API**
   - Click "Create API"
   - Choose "REST API" → "Build"
   - API name: `NutritionGPTBot-API`
   - Description: `API Gateway for NutritionGPT Bot`
   - Click "Create API"

3. **Create Resource**
   - Click "Actions" → "Create Resource"
   - Resource Name: `webhook`
   - Resource Path: `/webhook`
   - Click "Create Resource"

4. **Create Method**
   - Select the `/webhook` resource
   - Click "Actions" → "Create Method"
   - Select "POST" from dropdown
   - Click the checkmark ✓
   - Integration type: "Lambda Function"
   - Lambda Function: `NutritionGPTBot-v2`
   - Click "Save"
   - Click "OK" when prompted to grant permissions

5. **Deploy API**
   - Click "Actions" → "Deploy API"
   - Deployment stage: `[New Stage]`
   - Stage name: `prod`
   - Click "Deploy"

6. **Get Webhook URL**
   - Copy the "Invoke URL" shown
   - Your webhook URL will be: `[Invoke URL]/webhook`
   - Example: `https://abc123.execute-api.eu-north-1.amazonaws.com/prod/webhook`
   https://z0t1c04qm7.execute-api.eu-north-1.amazonaws.com/prod

## Step 2: Set Environment Variables

1. **Go to Lambda Console**
   - Navigate to: https://console.aws.amazon.com/lambda/
   - Select `NutritionGPTBot-v2`
   - Go to "Configuration" → "Environment variables"

2. **Add Variables**
   - Click "Edit"
   - Add these key-value pairs:
     - `TELEGRAM_BOT_TOKEN` = your actual bot token
     - `OPENAI_API_KEY` = your actual OpenAI API key
   - Click "Save"

## Step 3: Set Telegram Webhook

1. **Set Webhook URL**
   - Replace `[YOUR_BOT_TOKEN]` and `[WEBHOOK_URL]` in this URL:
   ```
   https://api.telegram.org/bot[YOUR_BOT_TOKEN]/setWebhook?url=[WEBHOOK_URL]
   https://api.telegram.org/bot8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc/setWebhook?url=https://z0t1c04qm7.execute-api.eu-north-1.amazonaws.com/prod

   https://api.telegram.org/bot8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc/getWebhookInfo

   https://api.telegram.org/bot8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc/setWebhook?url=https://z0t1c04qm7.execute-api.eu-north-1.amazonaws.com/prod/webhook

   https://api.telegram.org/bot8453520975:AAGa506SHTx5NlW_JAt11HlvztDACEkflFc/setWebhook?url=https://z0t1c04qm7.execute-api.eu-north-1.amazonaws.com/prod/webhook
   ```
   - Example:
   ```
   https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/setWebhook?url=https://abc123.execute-api.eu-north-1.amazonaws.com/prod/webhook
   ```
   - Open this URL in your browser or use curl

2. **Test Webhook**
   - Visit this URL to check webhook status:
   ```
   https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getWebhookInfo
   ```

## Step 4: Test Your Bot

1. **Send a message** to your bot on Telegram
2. **Check CloudWatch Logs** in AWS Console to see if it's working
3. **Stop your local bot** to avoid conflicts

## Troubleshooting

- **409 Conflict**: Make sure only one bot instance is running
- **Permission Denied**: Contact your AWS admin to grant API Gateway permissions
- **Webhook not working**: Check the webhook URL and Lambda function logs

## Quick Test Commands

```bash
# Test webhook (replace with your actual values)
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=YOUR_WEBHOOK_URL"

# Check webhook status
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
``` 

## 🔧 **Quick Fix - Add Pydantic Explicitly:**

### **Step 1: Update Requirements**
Add this line to your `requirements.txt`:
```
pydantic==2.5.0
```

### **Step 2: Redeploy**
```bash
python deploy_to_aws.py
```

This should force the installation of pydantic and its dependencies properly.

Try this approach - it should fix the missing pydantic_core issue! 🚀 