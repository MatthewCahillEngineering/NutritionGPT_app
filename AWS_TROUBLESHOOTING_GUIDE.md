# AWS Troubleshooting Guide - NutritionGPT Bot

This guide documents all the AWS deployment issues we encountered and their solutions during the development of NutritionGPT Bot v1.0.

## 🚨 Critical Issues & Solutions

### 1. Pydantic Dependency Conflicts

**Problem:**
```
Runtime.ImportModuleError: Unable to import module 'lambda_function': No module named 'pydantic_core._pydantic_core'
```

**Root Cause:**
- Complex dependencies like `pydantic` don't always install correctly in Lambda
- Lambda environment differs from local development
- Package conflicts between different versions

**Solution:**
- **Simplified approach**: Use only essential dependencies (`requests`)
- **Minimal requirements**: `requirements_simple.txt` with only `requests==2.31.0`
- **Clean deployment**: Fresh package creation each time

**Files:**
- `lambda_function_simple.py` - Simplified version without pydantic
- `requirements_simple.txt` - Minimal dependencies

### 2. Event Structure Misunderstanding

**Problem:**
```
[INFO] Not a valid Telegram update
```

**Root Cause:**
- Lambda receives Telegram updates directly, not wrapped in `body` field
- Code was looking for updates in wrong location
- API Gateway passes events directly to Lambda

**Solution:**
```python
# Check if event is already a Telegram update (direct invocation)
if 'update_id' in event and 'message' in event:
    telegram_update = event
    logger.info("Direct Telegram update detected")

# Check if event has body (API Gateway)
elif 'body' in event:
    body = json.loads(event['body'])
    if 'update_id' in body and 'message' in body:
        telegram_update = body
```

### 3. Webhook URL Configuration

**Problem:**
```
Wrong response from the webhook: 403 Forbidden
```

**Root Cause:**
- Webhook URL missing `/webhook` path
- API Gateway not properly configured
- Lambda permissions not set correctly

**Solution:**
- **Correct URL format**: `https://[API_ID].execute-api.eu-north-1.amazonaws.com/prod/webhook`
- **Manual API Gateway setup**: Follow `MANUAL_API_GATEWAY_SETUP.md`
- **Permission verification**: Check IAM roles

### 4. API Gateway Permission Issues

**Problem:**
```
AccessDeniedException: User is not authorized to perform: apigateway:POST
```

**Root Cause:**
- AWS user lacks API Gateway permissions
- Automated scripts fail due to permission restrictions

**Solution:**
- **Manual setup**: Create API Gateway through AWS Console
- **Permission request**: Contact AWS admin for API Gateway permissions
- **Alternative approach**: Use existing API Gateway if available

## 🔧 Deployment Issues & Fixes

### 1. Missing Dependencies in Lambda Package

**Problem:**
- Lambda function fails to import required modules
- Package size too large or missing files

**Solution:**
```bash
# Clean approach
rmdir /s lambda_package
mkdir lambda_package
pip install -r requirements_simple.txt -t lambda_package --upgrade
copy lambda_function_simple.py lambda_package\lambda_function.py
```

### 2. CloudWatch Logs Access

**Problem:**
```
Parameter validation failed: Unknown parameter in input: "maxItems"
```

**Solution:**
- Use `limit` instead of `maxItems` in CloudWatch API calls
- Check AWS SDK version compatibility

### 3. Lambda Function Timeout

**Problem:**
- Function times out during OpenAI API calls
- Slow response times

**Solution:**
- **Timeout setting**: 30 seconds (adequate for most requests)
- **Memory allocation**: 128 MB (sufficient for simple operations)
- **Error handling**: Graceful timeout handling

## 🛠️ Diagnostic Tools

### 1. Lambda Function Check
```bash
python check_lambda.py
```
- Checks function status and configuration
- Verifies environment variables
- Tests webhook endpoint

### 2. Quick Status Check
```bash
python simple_check.py
```
- Checks CloudWatch logs
- Tests Telegram webhook status
- Provides manual setup instructions

### 3. Webhook Testing
```bash
python test_webhook.py
```
- Tests webhook endpoint directly
- Sends sample Telegram updates
- Verifies response format

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI configured with correct region
- [ ] Environment variables set in Lambda
- [ ] API Gateway created and deployed
- [ ] Webhook URL configured in Telegram

### Deployment
- [ ] Clean package creation
- [ ] Dependencies installed correctly
- [ ] ZIP file created properly
- [ ] Lambda function updated successfully

### Post-Deployment
- [ ] Test webhook endpoint
- [ ] Send test message to bot
- [ ] Check CloudWatch logs
- [ ] Verify bot responses

## 🔍 Debugging Process

### 1. Check CloudWatch Logs
- Go to CloudWatch Console
- Navigate to `/aws/lambda/NutritionGPTBot-v2`
- Check latest log stream for errors

### 2. Test Webhook Status
```
https://api.telegram.org/bot[TOKEN]/getWebhookInfo
```

### 3. Test Lambda Directly
- Use diagnostic scripts
- Check function configuration
- Verify environment variables

### 4. Manual Verification
- Test API Gateway endpoint
- Check IAM permissions
- Verify webhook URL format

## 💡 Key Learnings

### 1. Lambda Best Practices
- **Keep dependencies minimal**: Only include essential packages
- **Use standard libraries**: Avoid complex third-party dependencies
- **Comprehensive logging**: Essential for debugging
- **Error handling**: Always handle exceptions gracefully

### 2. AWS Integration
- **Manual verification**: Often needed when automation fails
- **Permission management**: Critical for successful deployment
- **Event structure**: Understand how services pass data
- **Monitoring**: CloudWatch logs are invaluable

### 3. Telegram Bot Development
- **Webhook setup**: Requires HTTPS endpoint
- **Event processing**: Handle updates correctly
- **Response format**: Follow Telegram API requirements
- **Error handling**: Graceful failure handling

## 🚀 Production Readiness

### Current Status: ✅ Production Ready
- **Stable deployment**: Working consistently
- **Error handling**: Comprehensive logging and recovery
- **Scalability**: Serverless architecture
- **Monitoring**: CloudWatch integration

### Recommendations
- **Monitor usage**: Track function invocations and errors
- **Set up alerts**: CloudWatch alarms for failures
- **Regular updates**: Keep dependencies current
- **Backup strategy**: Version control and documentation

---

**This guide should help resolve most AWS deployment issues for future versions!** 🎯 