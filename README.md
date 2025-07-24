# NutritionGPT Bot v1.0

A Telegram bot that provides personalized nutrition advice, meal planning, and shopping list generation using OpenAI's GPT models.

## 🚀 Features

- **Meal Planning**: Generate personalized meal plans based on user preferences
- **Shopping Lists**: Create organized shopping lists from meal plans
- **Voice Commands**: Support for voice messages (transcription)
- **Nutrition Advice**: Get healthy eating tips and recommendations
- **Serverless Architecture**: Built on AWS Lambda for scalability

## 📋 Commands

- `/start` - Welcome message and bot introduction
- `/planmeals` - Generate a personalized meal plan
- `/shopping` - Create shopping list (coming soon)
- Voice messages - Say "plan meals" or similar phrases

## 🏗️ Architecture

### AWS Services Used
- **AWS Lambda**: Serverless function execution
- **API Gateway**: HTTP endpoint for webhook
- **CloudWatch**: Logging and monitoring
- **IAM**: Permissions and roles

### Key Components
- `lambda_function_simple.py` - Main Lambda function (v1.0)
- `lambda_function_v2.py` - Advanced version with full features
- Deployment scripts for easy updates
- Comprehensive logging and error handling

## 🚀 Deployment

### Prerequisites
- AWS CLI configured
- Python 3.12+
- Telegram Bot Token
- OpenAI API Key

### Quick Deploy
```bash
# Deploy simplified version (recommended)
python deploy_simple.py

# Deploy full version (if needed)
python deploy_to_aws.py
```

### Manual Setup
1. Create Lambda function in AWS Console
2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
3. Create API Gateway with `/webhook` endpoint
4. Set webhook URL in Telegram

## 📁 Project Structure

```
├── lambda_function_simple.py    # Main Lambda function (v1.0)
├── lambda_function_v2.py        # Advanced version
├── deploy_simple.py             # Simplified deployment script
├── deploy_to_aws.py             # Full deployment script
├── requirements_simple.txt      # Minimal dependencies
├── requirements.txt             # Full dependencies
├── DEPLOYMENT_LOG.md           # Deployment troubleshooting guide
├── MANUAL_API_GATEWAY_SETUP.md # Manual setup instructions
└── README.md                   # This file
```

## 🔧 Troubleshooting

### Common Issues
1. **Pydantic Dependencies**: Use `lambda_function_simple.py` to avoid dependency issues
2. **Webhook Setup**: Follow `MANUAL_API_GATEWAY_SETUP.md`
3. **Permission Errors**: Check IAM roles and user permissions
4. **Event Structure**: Lambda receives Telegram updates directly, not wrapped

### Debug Tools
- `check_lambda.py` - Comprehensive Lambda diagnostics
- `simple_check.py` - Quick status check
- `test_webhook.py` - Webhook testing
- CloudWatch logs for detailed error tracking

## 📊 Version History

### v1.0 (Current)
- ✅ Basic meal planning functionality
- ✅ Telegram integration working
- ✅ AWS Lambda deployment successful
- ✅ Simplified architecture for reliability
- ✅ Comprehensive error handling

### Planned Features
- Shopping list generation
- User preferences storage
- Advanced meal customization
- Nutritional analysis
- Recipe suggestions

## 🛠️ Development

### Local Testing
```bash
# Test the Lambda function locally
python lambda_function_simple.py

# Test webhook endpoint
python test_webhook.py
```

### Adding Features
1. Update `lambda_function_simple.py`
2. Test locally
3. Deploy with `python quick_deploy.py`
4. Monitor CloudWatch logs

## 📞 Support

For issues or questions:
1. Check CloudWatch logs first
2. Review `DEPLOYMENT_LOG.md` for common solutions
3. Test with diagnostic scripts
4. Check webhook status in Telegram

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**NutritionGPT Bot v1.0** - Making healthy eating easier, one meal at a time! 🍎🥗 