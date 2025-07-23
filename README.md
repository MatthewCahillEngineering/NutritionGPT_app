# NutritionGPT Bot

A Telegram bot that generates personalized meal plans and shopping lists using OpenAI's GPT-4 and Whisper for voice transcription.

## 🚀 Features

- **Meal Planning**: Generate personalized meal plans with nutrition information
- **Shopping Lists**: Automatically create shopping lists from meal plans
- **Voice Commands**: Send voice messages to plan meals
- **Nutrition Tracking**: Track protein and calorie content
- **Easy Setup**: Simple configuration with environment variables

## 📁 Project Structure

```
NutritionGPT_app/
├── bot_main.py          # Main bot application (working version)
├── ai_service.py        # OpenAI integration for meal plans and voice
├── config.py           # Environment variable configuration
├── requirements.txt    # Python dependencies
├── env_vars.txt       # Environment variables (API keys)
├── env_example.txt    # Example environment variables
├── README.md          # This file
├── QUICKSTART.md      # Quick start guide
└── .gitignore         # Git ignore rules
```

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `env_example.txt` to `env_vars.txt` and add your API keys:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the Bot
```bash
python bot_main.py
```

## 🎯 Usage

### Commands
- `/start` - Welcome message and instructions
- `/planmeals` - Generate a meal plan
- `/shopping` - Show current shopping list

### Voice Commands
- Send a voice message saying "plan meals" to generate a meal plan

## 🔧 Configuration

The bot uses environment variables for configuration:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `OPENAI_API_KEY`: Your OpenAI API key

## 📱 Bot Features

### Meal Planning
- Generates 3 meals (breakfast, lunch, dinner) + 1 snack
- Includes protein and calorie information
- Focuses on healthy, high-protein options

### Shopping Lists
- Automatically extracts ingredients from meal plans
- Removes duplicates and formats for easy reading
- Stores shopping lists per user

### Voice Integration
- Uses OpenAI Whisper for voice transcription
- Supports natural language commands
- Processes voice messages for meal planning

## 🚀 Quick Start

1. **Get API Keys**:
   - Telegram Bot Token: Message @BotFather on Telegram
   - OpenAI API Key: Sign up at https://platform.openai.com

2. **Set up environment**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure bot**:
   - Edit `env_vars.txt` with your API keys

4. **Run bot**:
   ```bash
   python bot_main.py
   ```

5. **Test bot**:
   - Find your bot on Telegram
   - Send `/start` to begin

## 💡 Tips

- The bot works best with clear voice commands
- Shopping lists are stored per user session
- Meal plans are generated fresh each time
- Voice transcription works with various accents

## 🔒 Security

- API keys are stored in `env_vars.txt` (not committed to git)
- Environment variables are loaded securely
- No sensitive data is logged

## 📞 Support

For issues or questions, check the logs in the terminal when running the bot. 