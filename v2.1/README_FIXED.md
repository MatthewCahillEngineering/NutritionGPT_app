# NutritionGPT Coach v2.1 - Fixed Version

## 🚀 What's Fixed

This is a **Lambda-compatible** version of the NutritionGPT Coach with enhanced memory and human-like conversation capabilities. The original v2.1 had several issues that prevented proper deployment to AWS Lambda.

### Key Fixes Made:

1. **🔧 Removed ChromaDB Dependency**
   - ChromaDB is not suitable for serverless environments
   - Replaced with DynamoDB/S3-based memory storage
   - Fallback to in-memory storage if AWS services unavailable

2. **💾 Lambda-Compatible Memory System**
   - `LambdaCompatibleMemoryManager` class
   - Uses DynamoDB for persistent storage
   - S3 as backup storage option
   - Simple keyword-based relevance scoring

3. **📦 Simplified Dependencies**
   - Removed problematic packages (ChromaDB, numpy, etc.)
   - Only essential Lambda-compatible packages
   - Reduced deployment package size

4. **🛡️ Enhanced Error Handling**
   - Graceful fallbacks when AWS services unavailable
   - Better exception handling throughout
   - More robust message processing

5. **🧠 Improved Memory Features**
   - Message type classification (meal_log, goal_check, advice, mood, casual)
   - Context-aware responses using past conversations
   - User profile persistence

## 📁 Files Overview

```
v2.1/
├── nutrition_coach_v2_1_fixed.py      # Main fixed application
├── requirements_fixed.txt             # Lambda-compatible dependencies
├── deploy_v2_1_fixed.py              # Deployment script
├── test_v2_1_fixed.py                # Test script
└── README_FIXED.md                   # This file
```

## 🚀 Quick Deployment

### Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Python 3.11** installed
3. **Environment variables set**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

### Deploy to AWS Lambda

1. **Run the deployment script**:
   ```bash
   cd v2.1
   python deploy_v2_1_fixed.py
   ```

2. **The script will**:
   - Install dependencies to a temporary directory
   - Create a deployment package
   - Deploy to AWS Lambda
   - Set up the Telegram webhook

3. **Expected output**:
   ```
   🚀 Starting NutritionGPT Coach v2.1 Fixed Deployment
   ==================================================
   Installing dependencies to temporary directory...
   Creating deployment package...
   Deploying to AWS Lambda...
   Successfully deployed NutritionGPTBot-v2-1-Fixed to AWS Lambda!
   Webhook set successfully!
   ✅ Deployment completed successfully!
   ```

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_v2_1_fixed.py
```

This will test:
- Data models
- Memory manager functionality
- Nutrition coach initialization
- Message classification

## 🔧 Configuration

### Environment Variables

The Lambda function expects these environment variables:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `OPENAI_API_KEY`: Your OpenAI API key

### AWS Services Used

1. **DynamoDB Table**: `nutrition_memories`
   - Automatically created if it doesn't exist
   - Stores conversation memories with user_id and timestamp

2. **S3 Bucket**: `nutrition-memories-bucket` (fallback)
   - Used if DynamoDB is unavailable
   - Stores memories as JSON files

### Lambda Function Configuration

- **Runtime**: Python 3.11
- **Handler**: `nutrition_coach_v2_1_fixed.lambda_handler`
- **Timeout**: 30 seconds
- **Memory**: 512 MB
- **Function Name**: `NutritionGPTBot-v2-1-Fixed`

## 🧠 Memory System Details

### How It Works

1. **Message Processing**:
   - User sends message
   - System classifies message type
   - Retrieves relevant past memories
   - Generates contextual response
   - Stores new memory

2. **Memory Storage**:
   - Primary: DynamoDB table
   - Backup: S3 bucket
   - Fallback: In-memory (temporary)

3. **Relevance Scoring**:
   - Simple keyword matching
   - Counts matching words between query and stored memories
   - Returns top-k most relevant memories

### Memory Types

- `meal_log`: Food and meal-related messages
- `goal_check`: Weight, goals, progress updates
- `advice`: Questions asking for help/recommendations
- `mood`: How user is feeling, energy levels
- `casual`: General conversation

## 🎯 Features

### Enhanced Personality
- More human-like, conversational responses
- Casual, friendly language
- Encouraging and positive tone
- Uses emojis appropriately

### Smart Memory
- Remembers user goals and preferences
- References past conversations naturally
- Builds on previous advice
- Context-aware responses

### User Management
- Persistent user profiles
- Meal logging and tracking
- Nutrition advice based on goals
- Progress tracking

## 🔍 Troubleshooting

### Common Issues

1. **"Missing environment variables"**
   - Ensure `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY` are set
   - Check AWS credentials are configured

2. **"DynamoDB not available"**
   - Check IAM permissions for DynamoDB
   - System will fall back to S3 or in-memory storage

3. **"Function deployment failed"**
   - Check AWS CLI configuration
   - Verify Lambda execution role permissions
   - Ensure deployment package size is under 50MB

4. **"Webhook setup failed"**
   - Check Telegram bot token is valid
   - Verify Lambda function URL is accessible
   - Check network connectivity

### Debug Mode

Enable detailed logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

### Expected Response Times
- **Cold start**: 2-5 seconds
- **Warm start**: 500ms-1 second
- **Memory retrieval**: 100-300ms

### Memory Usage
- **Base memory**: ~200MB
- **With dependencies**: ~400MB
- **Peak usage**: ~450MB

## 🔄 Updates

To update the deployed function:

1. Make your changes to `nutrition_coach_v2_1_fixed.py`
2. Run the deployment script again
3. The function will be updated in place

## 📞 Support

If you encounter issues:

1. Check the CloudWatch logs for the Lambda function
2. Run the test script locally
3. Verify all environment variables are set correctly
4. Check AWS service permissions

## 🎉 Success!

Once deployed, your bot will have:
- ✅ Lambda-compatible memory system
- ✅ Human-like conversation style
- ✅ Persistent user profiles
- ✅ Smart context awareness
- ✅ Reliable AWS deployment

The bot is now ready to provide personalized nutrition coaching with memory that persists across conversations! 