# 🤖 NutritionGPT - AI Nutrition Assistant Bot

A Telegram bot powered by OpenAI that generates personalized meal plans, manages shopping lists, and transcribes voice commands for nutrition planning.

## 🚀 Features

- **🍽️ AI Meal Planning**: Generate 1-7 day meal plans with protein-focused, healthy recipes
- **🛒 Smart Shopping Lists**: Automatically extract ingredients from meal plans
- **🎤 Voice Commands**: Send voice messages to plan meals and manage lists
- **📊 Nutrition Tracking**: Protein and calorie information for each meal
- **⚡ Real-time Processing**: Instant meal plan generation and voice transcription

## 🛠️ Tech Stack

- **Python 3.12+**
- **Telegram Bot API** (pyTelegramBotAPI)
- **OpenAI GPT-4** (Meal planning & voice transcription)
- **OpenAI Whisper** (Voice-to-text)
- **AWS Lambda** (Deployment ready)
- **DynamoDB** (Database ready)

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and help |
| `/planmeals` | Generate 1-day meal plan |
| `/planmeals 3` | Generate 3-day meal plan |
| `/voiceplan` | Send voice message for meal planning |
| `/shopping` | View shopping list |
| `/addtolist <item>` | Add item to shopping list |
| `/removetolist <item>` | Remove item from shopping list |
| `/clear` | Clear shopping list |

## 🎤 Voice Commands

- "Plan meals for today"
- "Create a 3-day meal plan"
- "Add chicken to shopping list"
- "I want high protein meals"

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Telegram Bot Token
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Ai_nutrition_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy env_vars.txt and add your API keys
   cp env_vars.txt .env
   # Edit .env with your actual API keys
   ```

4. **Run the bot**
   ```bash
   python bot_fixed.py
   ```

## 🔧 Configuration

Create a `.env` file with your API keys:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token_here

# AWS Configuration (for deployment)
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=nutrition_tracker
```

## 📁 Project Structure

```
Ai_nutrition_app/
├── bot_fixed.py          # Main bot application
├── ai_service.py         # OpenAI integration
├── config.py             # Configuration management
├── database.py           # Database operations (DynamoDB ready)
├── lambda_function.py    # AWS Lambda handler
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── env_vars.txt         # Environment variables template
```

## 🚀 Deployment

### Local Development
```bash
python bot_fixed.py
```

### AWS Lambda Deployment
1. Create Lambda function
2. Upload deployment package
3. Configure environment variables
4. Set up API Gateway for webhook

## 💡 Usage Examples

### Generate Meal Plan
```
User: /planmeals 3
Bot: 🍽️ Your 3-Day Meal Plan
     Day 1
     • Breakfast: Greek Yogurt Parfait
       📊 25g protein • 300 calories
       🥘 Greek yogurt, berries, almonds (+1 more)
```

### Voice Command
```
User: [Voice message] "Plan meals for today"
Bot: 🎤 You said: plan meals for today
     🍽️ Generating your 1-day meal plan...
     [Meal plan response]
     🛒 Shopping list updated! Use /shopping to view it.
```

## 🔒 Security

- API keys stored in environment variables
- No hardcoded secrets in code
- Secure voice file handling
- Input validation and sanitization

## 📈 Future Enhancements

- [ ] User preferences and dietary restrictions
- [ ] Meal plan history and favorites
- [ ] Nutritional goal tracking
- [ ] Recipe sharing and community features
- [ ] Integration with grocery delivery services
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

---

**Version**: v0.1.0  
**Last Updated**: July 2024  
**Status**: ✅ Production Ready 