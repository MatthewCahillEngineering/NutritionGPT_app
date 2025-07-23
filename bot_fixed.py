import telebot
import json
import os
import tempfile
from datetime import datetime
from config import TELEGRAM_TOKEN, validate_config
from ai_service import AIService

# Simple local storage (in-memory for testing)
local_storage = {}

class FixedNutritionBot:
    def __init__(self):
        # Validate configuration
        validate_config()
        
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.ai_service = AIService()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot command and message handlers"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = """
🤖 Welcome to NutritionGPT! Your AI Nutrition Assistant

📋 Available Commands:
/planmeals - Generate a meal plan (1-7 days)
/planmeals 3 - Generate 3-day meal plan
/voiceplan - Send voice message to plan meals
/shopping - View your shopping list
/addtolist <item> - Add item to shopping list
/removetolist <item> - Remove item from shopping list
/clear - Clear shopping list
/help - Show this help message

🎤 Voice Commands:
- "Plan meals for today"
- "Create a 3-day meal plan"
- "Add chicken to shopping list"
- "I want high protein meals"

Start by typing /planmeals or send a voice message!
            """
            self.bot.reply_to(message, welcome_text)
        
        @self.bot.message_handler(commands=['planmeals'])
        def handle_meal_plan_command(message):
            try:
                print(f"Processing meal plan command from user {message.from_user.id}")
                
                # Parse days from command
                args = message.text.split()
                days = 1
                if len(args) > 1:
                    try:
                        days = int(args[1])
                        days = max(1, min(days, 7))  # Limit to 1-7 days
                    except ValueError:
                        days = 1
                
                self.bot.reply_to(message, f"🍽️ Generating your {days}-day meal plan... Please wait!")
                
                # Generate meal plan
                print("Calling AI service to generate meal plan...")
                meal_plan_json = self.ai_service.generate_meal_plan(days=days)
                
                if meal_plan_json:
                    print("Meal plan generated successfully")
                    # Save to local storage
                    user_id = str(message.from_user.id)
                    if user_id not in local_storage:
                        local_storage[user_id] = {}
                    local_storage[user_id]['meal_plan'] = meal_plan_json
                    
                    # Format and send meal plan
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
                                    item = item[1:]
                                if item:  # Check again after removing dash
                                    self.add_to_shopping_list(message.from_user.id, item)
                                    print(f"Added to shopping list: {item}")
                    
                    self.bot.reply_to(message, "🛒 Shopping list updated! Use /shopping to view it.")
                else:
                    print("Failed to generate meal plan")
                    self.bot.reply_to(message, "❌ Sorry, I couldn't generate a meal plan. Please try again.")
                    
            except Exception as e:
                print(f"Error in meal plan command: {e}")
                import traceback
                traceback.print_exc()
                self.bot.reply_to(message, "❌ An error occurred. Please try again.")
        
        @self.bot.message_handler(commands=['voiceplan'])
        def handle_voice_plan_command(message):
            self.bot.reply_to(message, "🎤 Please send a voice message with your meal planning request!")
        
        @self.bot.message_handler(content_types=['voice'])
        def handle_voice_message(message):
            try:
                print(f"Processing voice message from user {message.from_user.id}")
                self.bot.reply_to(message, "🎤 Processing your voice message...")
                
                # Download voice file
                print("Downloading voice file...")
                voice_file_path = self.ai_service.download_voice_file(
                    message.voice.file_id, 
                    TELEGRAM_TOKEN
                )
                
                if not voice_file_path:
                    print("Failed to download voice file")
                    self.bot.reply_to(message, "❌ Could not download voice file. Please try again.")
                    return
                
                # Transcribe voice
                print("Transcribing voice...")
                transcript = self.ai_service.transcribe_voice(voice_file_path)
                
                # Clean up temp file
                try:
                    os.unlink(voice_file_path)
                except:
                    pass
                
                if not transcript:
                    print("Failed to transcribe voice")
                    self.bot.reply_to(message, "❌ Could not transcribe voice. Please try again.")
                    return
                
                print(f"Voice transcribed: {transcript}")
                self.bot.reply_to(message, f"🎤 You said: {transcript}")
                
                # Process transcript
                self.process_voice_command(message, transcript)
                
            except Exception as e:
                print(f"Error handling voice message: {e}")
                import traceback
                traceback.print_exc()
                self.bot.reply_to(message, "❌ An error occurred processing your voice message.")
        
        @self.bot.message_handler(commands=['shopping'])
        def handle_shopping_list(message):
            try:
                items = self.get_shopping_list(message.from_user.id)
                if items:
                    shopping_text = "🛒 Your Shopping List:\n\n"
                    for i, item in enumerate(items, 1):
                        shopping_text += f"{i}. {item}\n"
                    self.bot.reply_to(message, shopping_text)
                else:
                    self.bot.reply_to(message, "🛒 Your shopping list is empty. Generate a meal plan to get started!")
            except Exception as e:
                print(f"Error getting shopping list: {e}")
                self.bot.reply_to(message, "❌ Error retrieving shopping list.")
        
        @self.bot.message_handler(commands=['addtolist'])
        def handle_add_to_list(message):
            try:
                item = message.text.replace('/addtolist', '').strip()
                if item:
                    self.add_to_shopping_list(message.from_user.id, item)
                    self.bot.reply_to(message, f"✅ Added '{item}' to your shopping list!")
                else:
                    self.bot.reply_to(message, "❌ Please specify an item to add. Example: /addtolist chicken breast")
            except Exception as e:
                print(f"Error adding to shopping list: {e}")
                self.bot.reply_to(message, "❌ Error adding item to shopping list.")
        
        @self.bot.message_handler(commands=['removetolist'])
        def handle_remove_from_list(message):
            try:
                item = message.text.replace('/removetolist', '').strip()
                if item:
                    self.remove_from_shopping_list(message.from_user.id, item)
                    self.bot.reply_to(message, f"✅ Removed '{item}' from your shopping list!")
                else:
                    self.bot.reply_to(message, "❌ Please specify an item to remove. Example: /removetolist chicken breast")
            except Exception as e:
                print(f"Error removing from shopping list: {e}")
                self.bot.reply_to(message, "❌ Error removing item from shopping list.")
        
        @self.bot.message_handler(commands=['clear'])
        def handle_clear_list(message):
            try:
                self.save_shopping_list(message.from_user.id, [])
                self.bot.reply_to(message, "🗑️ Shopping list cleared!")
            except Exception as e:
                print(f"Error clearing shopping list: {e}")
                self.bot.reply_to(message, "❌ Error clearing shopping list.")
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text_message(message):
            # Handle regular text messages
            text = message.text.lower()
            
            if any(keyword in text for keyword in ['meal plan', 'plan meals', 'food plan']):
                self.bot.reply_to(message, "🍽️ Use /planmeals to generate a meal plan!")
            elif any(keyword in text for keyword in ['shopping', 'grocery', 'list']):
                self.bot.reply_to(message, "🛒 Use /shopping to view your shopping list!")
            else:
                self.bot.reply_to(message, "💬 I didn't understand that. Try /help for available commands!")
    
    def process_voice_command(self, message, transcript):
        """Process voice command transcript"""
        try:
            # Check for meal planning requests
            if any(keyword in transcript for keyword in ['plan meal', 'meal plan', 'food plan', 'create meal']):
                days = 1
                if '3 day' in transcript or 'three day' in transcript:
                    days = 3
                elif '7 day' in transcript or 'week' in transcript:
                    days = 7
                elif '2 day' in transcript or 'two day' in transcript:
                    days = 2
                
                self.bot.reply_to(message, f"🍽️ Generating your {days}-day meal plan...")
                
                meal_plan_json = self.ai_service.generate_meal_plan(days=days)
                if meal_plan_json:
                    # Save to local storage
                    user_id = str(message.from_user.id)
                    if user_id not in local_storage:
                        local_storage[user_id] = {}
                    local_storage[user_id]['meal_plan'] = meal_plan_json
                    
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
                            if item:  # Accept all non-empty items
                                # Remove leading dash and space if present
                                if item.startswith('- '):
                                    item = item[2:]
                                elif item.startswith('-'):
                                    item = item[1:]
                                if item:  # Check again after removing dash
                                    self.add_to_shopping_list(message.from_user.id, item)
                                    print(f"Added to shopping list: {item}")
                    
                    self.bot.reply_to(message, "🛒 Shopping list updated! Use /shopping to view it.")
                else:
                    self.bot.reply_to(message, "❌ Could not generate meal plan. Please try again.")
            
            # Check for shopping list requests
            elif any(keyword in transcript for keyword in ['add to list', 'shopping list', 'grocery list']):
                # Extract item from transcript
                words = transcript.split()
                try:
                    add_index = words.index('add')
                    if add_index + 2 < len(words):
                        item = ' '.join(words[add_index + 2:])
                        self.add_to_shopping_list(message.from_user.id, item)
                        self.bot.reply_to(message, f"✅ Added '{item}' to your shopping list!")
                    else:
                        self.bot.reply_to(message, "❌ Please specify what to add to the shopping list.")
                except ValueError:
                    self.bot.reply_to(message, "❌ Please specify what to add to the shopping list.")
            
            else:
                self.bot.reply_to(message, "💬 I didn't understand that voice command. Try saying 'plan meals' or 'add chicken to list'")
                
        except Exception as e:
            print(f"Error processing voice command: {e}")
            self.bot.reply_to(message, "❌ Error processing your voice command.")
    
    def format_meal_plan(self, meal_plan_json, days):
        """Format meal plan for display"""
        try:
            # Try to parse JSON - handle both string and dict inputs
            if isinstance(meal_plan_json, str):
                # Remove any markdown code blocks if present
                if meal_plan_json.startswith('```json'):
                    meal_plan_json = meal_plan_json.replace('```json', '').replace('```', '').strip()
                elif meal_plan_json.startswith('```'):
                    meal_plan_json = meal_plan_json.replace('```', '').strip()
                
                meal_plan = json.loads(meal_plan_json)
            else:
                meal_plan = meal_plan_json
            
            formatted_text = f"🍽️ <b>Your {days}-Day Meal Plan</b>\n\n"
            
            for day_data in meal_plan.get('days', []):
                day_num = day_data.get('day', 1)
                formatted_text += f"<b>Day {day_num}</b>\n"
                
                for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                    meal = day_data.get(meal_type, {})
                    if meal:
                        name = meal.get('name', 'Unknown')
                        protein = meal.get('protein', 'N/A')
                        calories = meal.get('calories', 'N/A')
                        ingredients = meal.get('ingredients', [])
                        
                        # Format ingredients nicely
                        if ingredients:
                            ingredients_text = ', '.join(ingredients[:3])  # Show first 3 ingredients
                            if len(ingredients) > 3:
                                ingredients_text += f" (+{len(ingredients)-3} more)"
                        else:
                            ingredients_text = "Ingredients not specified"
                        
                        formatted_text += f"• <b>{meal_type.title()}:</b> {name}\n"
                        formatted_text += f"  📊 {protein} protein • {calories} calories\n"
                        formatted_text += f"  🥘 {ingredients_text}\n\n"
                
                formatted_text += "\n"
            
            return formatted_text
            
        except Exception as e:
            print(f"Error formatting meal plan: {e}")
            print(f"Raw meal plan: {meal_plan_json}")
            # Fallback: return a simple formatted version
            try:
                if isinstance(meal_plan_json, str):
                    # Try to extract just the meal names
                    import re
                    meal_names = re.findall(r'"name":\s*"([^"]+)"', meal_plan_json)
                    if meal_names:
                        formatted_text = f"🍽️ <b>Your {days}-Day Meal Plan</b>\n\n"
                        formatted_text += "<b>Day 1</b>\n"
                        meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
                        for i, name in enumerate(meal_names[:4]):
                            formatted_text += f"• <b>{meal_types[i]}:</b> {name}\n"
                        return formatted_text
            except:
                pass
            
            return "🍽️ Here's your meal plan!\n\n" + str(meal_plan_json)
    
    # Local storage methods
    def get_shopping_list(self, user_id):
        """Get shopping list for user"""
        user_id_str = str(user_id)
        if user_id_str in local_storage and 'shopping_list' in local_storage[user_id_str]:
            return local_storage[user_id_str]['shopping_list']
        return []
    
    def save_shopping_list(self, user_id, items):
        """Save shopping list for user"""
        user_id_str = str(user_id)
        if user_id_str not in local_storage:
            local_storage[user_id_str] = {}
        local_storage[user_id_str]['shopping_list'] = items
        return True
    
    def add_to_shopping_list(self, user_id, item):
        """Add item to shopping list"""
        current_list = self.get_shopping_list(user_id)
        if item not in current_list:
            current_list.append(item)
            return self.save_shopping_list(user_id, current_list)
        return True
    
    def remove_from_shopping_list(self, user_id, item):
        """Remove item from shopping list"""
        current_list = self.get_shopping_list(user_id)
        if item in current_list:
            current_list.remove(item)
            return self.save_shopping_list(user_id, current_list)
        return True
    
    def run(self):
        """Start the bot"""
        print("🤖 Starting NutritionGPT Bot (v1.0)...")
        print("📱 Your bot is ready at: t.me/NutritionGPTAI_bot")
        print("💡 Test commands: /start, /planmeals, /shopping")
        print("🎤 Voice commands: Send voice message saying 'plan meals'")
        print("⏹️  Press Ctrl+C to stop the bot")
        
        try:
            # Start polling
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    bot = FixedNutritionBot()
    bot.run() 