#!/usr/bin/env python3
"""
NutritionGPT Bot - Fixed Version with Lambda Support
Handles meal planning, shopping lists, and voice commands
"""
import telebot
import json
import os
import logging
from ai_service import AIService
from config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionGPTBot:
    def __init__(self, config):
        """Initialize the bot with configuration"""
        self.config = config
        self.bot = telebot.TeleBot(config['telegram_bot_token'])
        self.ai_service = AIService(config['openai_api_key'])
        
        # Local storage for user data (in production, use DynamoDB)
        self.local_storage = {}
        
        # Set up message handlers
        self.setup_handlers()
        
        logger.info("🤖 NutritionGPT Bot initialized successfully")
    
    def setup_handlers(self):
        """Set up message handlers"""
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start(message):
            self.handle_start_command(message)
        
        @self.bot.message_handler(commands=['planmeals'])
        def handle_plan_meals(message):
            self.handle_meal_plan_command(message)
        
        @self.bot.message_handler(commands=['shopping'])
        def handle_shopping(message):
            self.handle_shopping_list(message)
        
        @self.bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            self.handle_voice_message(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message):
            self.handle_text_message(message)
    
    def process_message(self, webhook_data):
        """Process message from Lambda webhook"""
        try:
            # Extract message from webhook data
            if 'message' in webhook_data:
                message_data = webhook_data['message']
            else:
                message_data = webhook_data
                
            # Create a message object from the webhook data
            message = telebot.types.Message.de_json(message_data)
            
            # Process based on content type
            if message.voice:
                self.handle_voice_message(message)
            elif message.text:
                if message.text.startswith('/'):
                    self.handle_command(message)
                else:
                    self.handle_text_message(message)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Error processing message"
        
        return "OK"
    
    def process_callback_query(self, webhook_data):
        """Process callback queries from Lambda webhook"""
        try:
            # Extract callback query from webhook data
            if 'callback_query' in webhook_data:
                callback_data = webhook_data['callback_query']
            else:
                callback_data = webhook_data
                
            callback_query = telebot.types.CallbackQuery.de_json(callback_data)
            # Handle callback queries if needed
            logger.info(f"Received callback query: {callback_query.data}")
        except Exception as e:
            logger.error(f"Error processing callback query: {e}")
            return "Error processing callback query"
        
        return "OK"
    
    def handle_command(self, message):
        """Handle bot commands"""
        command = message.text.split()[0].lower()
        
        if command in ['/start', '/help']:
            self.handle_start_command(message)
        elif command == '/planmeals':
            self.handle_meal_plan_command(message)
        elif command == '/shopping':
            self.handle_shopping_list(message)
        else:
            self.bot.reply_to(message, "❓ Unknown command. Use /help for available commands.")
    
    def handle_start_command(self, message):
        """Handle /start command"""
        welcome_message = """
🤖 **Welcome to NutritionGPT!**

I'm your AI nutrition assistant. Here's what I can do:

🍽️ **Meal Planning**
• `/planmeals` - Generate a 1-7 day meal plan
• Voice command: "plan meals" or "create meal plan"

🛒 **Shopping Lists**
• `/shopping` - View your shopping list
• Automatically created from meal plans

🎤 **Voice Commands**
• Send voice messages for hands-free operation
• "Plan meals for 3 days"
• "Add eggs to shopping list"

💡 **Tips**
• Focus on high-protein, healthy meals
• Get detailed nutrition info
• Manage ingredients automatically

Ready to start? Try `/planmeals` or send a voice message!
        """
        self.bot.reply_to(message, welcome_message, parse_mode='HTML')
    
    def handle_meal_plan_command(self, message):
        """Handle meal plan generation"""
        try:
            print(f"Processing meal plan command from user {message.from_user.id}")
            
            # Parse days from command (default to 1 day)
            text = message.text.lower()
            days = 1
            if 'day' in text or 'days' in text:
                import re
                day_match = re.search(r'(\d+)\s*day', text)
                if day_match:
                    days = min(int(day_match.group(1)), 7)  # Max 7 days
            
            self.bot.reply_to(message, f"🍽️ Generating {days}-day meal plan... Please wait.")
            
            print("Calling AI service to generate meal plan...")
            meal_plan_json = self.ai_service.generate_meal_plan(days=days)
            
            if meal_plan_json:
                print("Meal plan generated successfully")
                
                # Save to local storage
                user_id = str(message.from_user.id)
                if user_id not in self.local_storage:
                    self.local_storage[user_id] = {}
                self.local_storage[user_id]['meal_plan'] = meal_plan_json
                
                formatted_plan = self.format_meal_plan(meal_plan_json, days)
                self.bot.reply_to(message, formatted_plan, parse_mode='HTML')
                
                # Generate shopping list
                print("Generating shopping list...")
                shopping_items = self.ai_service.extract_shopping_items(meal_plan_json)
                if shopping_items:
                    print(f"Shopping items received: {shopping_items}")
                    items_list = shopping_items.split('\n')
                    for item in items_list:
                        item = item.strip()
                        if item:  # Remove the dash check - accept all non-empty items
                            # Remove leading dash and space if present
                            if item.startswith('- '):
                                item = item[2:]
                            elif item.startswith('-'):
                                item = item[1:].strip()
                            
                            # Add to user's shopping list
                            if user_id not in self.local_storage:
                                self.local_storage[user_id] = {}
                            if 'shopping_list' not in self.local_storage[user_id]:
                                self.local_storage[user_id]['shopping_list'] = []
                            
                            if item not in self.local_storage[user_id]['shopping_list']:
                                self.local_storage[user_id]['shopping_list'].append(item)
                                print(f"Added to shopping list: {item}")
                    
                    self.bot.reply_to(message, "🛒 Shopping list updated with meal plan ingredients!")
                else:
                    print("No shopping items received")
                    self.bot.reply_to(message, "⚠️ Could not generate shopping list from meal plan.")
            else:
                print("Failed to generate meal plan")
                self.bot.reply_to(message, "❌ Sorry, I couldn't generate a meal plan right now. Please try again.")
                
        except Exception as e:
            print(f"Error generating meal plan: {e}")
            self.bot.reply_to(message, "❌ Sorry, there was an error generating your meal plan. Please try again.")
    
    def handle_voice_message(self, message):
        """Handle voice messages"""
        try:
            print(f"Processing voice message from user {message.from_user.id}")
            
            # Download and transcribe voice
            print("Downloading voice file...")
            file_info = self.bot.get_file(message.voice.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            
            print("Transcribing voice...")
            transcription = self.ai_service.transcribe_voice(downloaded_file)
            
            if transcription:
                print(f"Voice transcribed: {transcription}")
                transcription_lower = transcription.lower()
                
                # Check for meal planning keywords
                if any(keyword in transcription_lower for keyword in ['plan', 'meal', 'food', 'diet']):
                    # Extract number of days if mentioned
                    days = 1
                    import re
                    day_match = re.search(r'(\d+)\s*day', transcription_lower)
                    if day_match:
                        days = min(int(day_match.group(1)), 7)
                    
                    self.bot.reply_to(message, f"🎤 Heard: '{transcription}'\n🍽️ Generating {days}-day meal plan...")
                    
                    meal_plan_json = self.ai_service.generate_meal_plan(days=days)
                    if meal_plan_json:
                        # Save to local storage
                        user_id = str(message.from_user.id)
                        if user_id not in self.local_storage:
                            self.local_storage[user_id] = {}
                        self.local_storage[user_id]['meal_plan'] = meal_plan_json
                        
                        formatted_plan = self.format_meal_plan(meal_plan_json, days)
                        self.bot.reply_to(message, formatted_plan, parse_mode='HTML')
                        
                        # Generate shopping list
                        print("Generating shopping list from voice command...")
                        shopping_items = self.ai_service.extract_shopping_items(meal_plan_json)
                        if shopping_items:
                            print(f"Shopping items received: {shopping_items}")
                            items_list = shopping_items.split('\n')
                            for item in items_list:
                                item = item.strip()
                                if item:  # Remove the dash check - accept all non-empty items
                                    # Remove leading dash and space if present
                                    if item.startswith('- '):
                                        item = item[2:]
                                    elif item.startswith('-'):
                                        item = item[1:].strip()
                                    
                                    # Add to user's shopping list
                                    if user_id not in self.local_storage:
                                        self.local_storage[user_id] = {}
                                    if 'shopping_list' not in self.local_storage[user_id]:
                                        self.local_storage[user_id]['shopping_list'] = []
                                    
                                    if item not in self.local_storage[user_id]['shopping_list']:
                                        self.local_storage[user_id]['shopping_list'].append(item)
                                        print(f"Added to shopping list: {item}")
                            
                            self.bot.reply_to(message, "🛒 Shopping list updated with meal plan ingredients!")
                        else:
                            print("No shopping items received")
                            self.bot.reply_to(message, "⚠️ Could not generate shopping list from meal plan.")
                    else:
                        self.bot.reply_to(message, "❌ Sorry, I couldn't generate a meal plan. Please try again.")
                else:
                    self.bot.reply_to(message, f"🎤 I heard: '{transcription}'\n\n💡 Try saying 'plan meals' or 'create meal plan' to get started!")
            else:
                print("Failed to transcribe voice")
                self.bot.reply_to(message, "❌ Sorry, I couldn't understand your voice message. Please try again.")
                
        except Exception as e:
            print(f"Error transcribing voice: {e}")
            self.bot.reply_to(message, "❌ Sorry, there was an error processing your voice message. Please try again.")
    
    def handle_shopping_list(self, message):
        """Handle shopping list display"""
        user_id = str(message.from_user.id)
        
        if user_id in self.local_storage and 'shopping_list' in self.local_storage[user_id]:
            shopping_list = self.local_storage[user_id]['shopping_list']
            if shopping_list:
                list_text = "🛒 **Your Shopping List:**\n\n"
                for i, item in enumerate(shopping_list, 1):
                    list_text += f"{i}. {item}\n"
                self.bot.reply_to(message, list_text, parse_mode='HTML')
            else:
                self.bot.reply_to(message, "🛒 Your shopping list is empty.\n\n💡 Generate a meal plan with `/planmeals` to add ingredients!")
        else:
            self.bot.reply_to(message, "🛒 Your shopping list is empty.\n\n💡 Generate a meal plan with `/planmeals` to add ingredients!")
    
    def handle_text_message(self, message):
        """Handle general text messages"""
        text = message.text.lower()
        
        if any(keyword in text for keyword in ['meal', 'food', 'plan', 'diet']):
            self.bot.reply_to(message, "🍽️ To generate a meal plan, use `/planmeals` or send a voice message saying 'plan meals'!")
        else:
            self.bot.reply_to(message, "💡 I'm here to help with your nutrition! Try:\n• `/planmeals` - Generate meal plans\n• `/shopping` - View shopping list\n• Send voice messages for hands-free operation")
    
    def format_meal_plan(self, meal_plan_json, days):
        """Format meal plan for display"""
        try:
            # Parse JSON if it's a string
            if isinstance(meal_plan_json, str):
                # Remove markdown code blocks if present
                if meal_plan_json.startswith('```json'):
                    meal_plan_json = meal_plan_json[7:]
                if meal_plan_json.endswith('```'):
                    meal_plan_json = meal_plan_json[:-3]
                
                meal_plan = json.loads(meal_plan_json.strip())
            else:
                meal_plan = meal_plan_json
            
            formatted_text = f"🍽️ **{days}-Day Meal Plan**\n\n"
            
            for day_data in meal_plan.get('days', []):
                day_num = day_data.get('day', 1)
                formatted_text += f"**Day {day_num}**\n"
                
                meals = ['breakfast', 'lunch', 'dinner', 'snack']
                for meal in meals:
                    if meal in day_data:
                        meal_info = day_data[meal]
                        name = meal_info.get('name', 'Unknown')
                        protein = meal_info.get('protein', 'N/A')
                        calories = meal_info.get('calories', 'N/A')
                        
                        formatted_text += f"• **{meal.title()}**: {name}\n"
                        formatted_text += f"  Protein: {protein} | Calories: {calories}\n"
                
                formatted_text += "\n"
            
            return formatted_text
            
        except Exception as e:
            print(f"Error formatting meal plan: {e}")
            return f"🍽️ **{days}-Day Meal Plan Generated!**\n\n✅ Your meal plan has been created and shopping list updated.\n\n💡 Use `/shopping` to view your ingredients list."
    
    def set_webhook(self, webhook_url=None):
        """Set Telegram webhook URL"""
        try:
            if webhook_url is None:
                # Get the Lambda function URL from environment or construct it
                import boto3
                lambda_client = boto3.client('lambda')
                function_name = 'NutritionGPTBot'
                
                try:
                    response = lambda_client.get_function_url_config(FunctionName=function_name)
                    webhook_url = response['FunctionUrl']
                except:
                    # Fallback: construct the URL
                    webhook_url = f"https://x64pdv7ny2palphmykupnu2fwe0mjpvz.lambda-url.us-east-1.on.aws/"
            
            result = self.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set successfully: {result}")
            return True
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    def run_polling(self):
        """Run bot in polling mode (for local development)"""
        print("🤖 Starting NutritionGPT Bot (Fixed Version)...")
        print("📱 Your bot is ready at: t.me/NutritionGPTAI_bot")
        print("💡 Test commands: /start, /planmeals, /shopping")
        print("🎤 Voice commands: Send voice message saying 'plan meals'")
        print("⏹️  Press Ctrl+C to stop the bot")
        
        try:
            self.bot.polling(none_stop=True, timeout=60)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")

def main():
    """Main function to run the bot"""
    try:
        # Load configuration
        config = load_config()
        
        # Create and run bot
        bot = NutritionGPTBot(config)
        bot.run_polling()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main() 