import json
import logging
import os
import tempfile
import requests
import openai
import telebot
from telebot import types

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Initialize Telegram bot
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))

# Local storage (in production, use DynamoDB)
local_storage = {}

def transcribe_voice(voice_file_path):
    """Transcribe voice message using OpenAI Whisper"""
    try:
        with open(voice_file_path, 'rb') as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text.lower()
    except Exception as e:
        logger.error(f"Error transcribing voice: {e}")
        return None

def generate_meal_plan(user_preferences="", days=1):
    """Generate meal plan using OpenAI GPT"""
    try:
        prompt = f"""
        Create a {days}-day meal plan with 3 meals (breakfast, lunch, dinner) and 1 snack per day.
        Focus on high protein, healthy, and delicious meals.
        
        User preferences: {user_preferences if user_preferences else "No specific preferences"}
        
        Format the response as a JSON object with this structure:
        {{
            "days": [
                {{
                    "day": 1,
                    "breakfast": {{"name": "meal name", "ingredients": ["ingredient1", "ingredient2"], "protein": "XXg", "calories": "XXX"}},
                    "lunch": {{"name": "meal name", "ingredients": ["ingredient1", "ingredient2"], "protein": "XXg", "calories": "XXX"}},
                    "dinner": {{"name": "meal name", "ingredients": ["ingredient1", "ingredient2"], "protein": "XXg", "calories": "XXX"}},
                    "snack": {{"name": "snack name", "ingredients": ["ingredient1", "ingredient2"], "protein": "XXg", "calories": "XXX"}}
                }}
            ]
        }}
        
        Make sure each meal has at least 20g of protein and is practical to cook.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutrition expert and meal planner. Provide healthy, protein-rich meal plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating meal plan: {e}")
        return None

def extract_shopping_items(meal_plan_text):
    """Extract shopping list items from meal plan"""
    try:
        prompt = f"""
        Extract all unique ingredients needed for this meal plan. 
        Combine similar items and provide quantities.
        
        Meal plan: {meal_plan_text}
        
        Return as a simple list of items, one per line, with quantities where appropriate.
        Example:
        - 2 lbs chicken breast
        - 1 dozen eggs
        - 1 lb spinach
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts shopping list items from meal plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error extracting shopping items: {e}")
        return None

def format_meal_plan(meal_plan_json, days):
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
        logger.error(f"Error formatting meal plan: {e}")
        return f"🍽️ **{days}-Day Meal Plan Generated!**\n\n✅ Your meal plan has been created and shopping list updated.\n\n💡 Use `/shopping` to view your ingredients list."

def process_message(message_data):
    """Process incoming message"""
    try:
        # Create a message object from the webhook data
        message = types.Message.de_json(message_data)
        
        # Handle different message types
        if message.voice:
            return handle_voice_message(message)
        elif message.text:
            if message.text.startswith('/'):
                return handle_command(message)
            else:
                return handle_text_message(message)
        
        return "OK"
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return "Error processing message"

def handle_command(message):
    """Handle bot commands"""
    command = message.text.split()[0].lower()
    
    if command in ['/start', '/help']:
        return handle_start_command(message)
    elif command == '/planmeals':
        return handle_meal_plan_command(message)
    elif command == '/shopping':
        return handle_shopping_list(message)
    else:
        bot.reply_to(message, "❓ Unknown command. Use /help for available commands.")
        return "OK"

def handle_start_command(message):
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
    bot.reply_to(message, welcome_message, parse_mode='HTML')
    return "OK"

def handle_meal_plan_command(message):
    """Handle meal plan generation"""
    try:
        logger.info(f"Processing meal plan command from user {message.from_user.id}")
        
        # Parse days from command (default to 1 day)
        text = message.text.lower()
        days = 1
        if 'day' in text or 'days' in text:
            import re
            day_match = re.search(r'(\d+)\s*day', text)
            if day_match:
                days = min(int(day_match.group(1)), 7)  # Max 7 days
        
        bot.reply_to(message, f"🍽️ Generating {days}-day meal plan... Please wait.")
        
        logger.info("Calling AI service to generate meal plan...")
        meal_plan_json = generate_meal_plan(days=days)
        
        if meal_plan_json:
            logger.info("Meal plan generated successfully")
            
            # Save to local storage
            user_id = str(message.from_user.id)
            if user_id not in local_storage:
                local_storage[user_id] = {}
            local_storage[user_id]['meal_plan'] = meal_plan_json
            
            formatted_plan = format_meal_plan(meal_plan_json, days)
            bot.reply_to(message, formatted_plan, parse_mode='HTML')
            
            # Generate shopping list
            logger.info("Generating shopping list...")
            shopping_items = extract_shopping_items(meal_plan_json)
            if shopping_items:
                logger.info(f"Shopping items received: {shopping_items}")
                items_list = shopping_items.split('\n')
                for item in items_list:
                    item = item.strip()
                    if item:
                        # Remove leading dash and space if present
                        if item.startswith('- '):
                            item = item[2:]
                        elif item.startswith('-'):
                            item = item[1:].strip()
                        
                        # Add to user's shopping list
                        if user_id not in local_storage:
                            local_storage[user_id] = {}
                        if 'shopping_list' not in local_storage[user_id]:
                            local_storage[user_id]['shopping_list'] = []
                        
                        if item not in local_storage[user_id]['shopping_list']:
                            local_storage[user_id]['shopping_list'].append(item)
                            logger.info(f"Added to shopping list: {item}")
                
                bot.reply_to(message, "🛒 Shopping list updated with meal plan ingredients!")
            else:
                logger.info("No shopping items received")
                bot.reply_to(message, "⚠️ Could not generate shopping list from meal plan.")
        else:
            logger.info("Failed to generate meal plan")
            bot.reply_to(message, "❌ Sorry, I couldn't generate a meal plan right now. Please try again.")
            
    except Exception as e:
        logger.error(f"Error generating meal plan: {e}")
        bot.reply_to(message, "❌ Sorry, there was an error generating your meal plan. Please try again.")
    
    return "OK"

def handle_voice_message(message):
    """Handle voice messages"""
    try:
        logger.info(f"Processing voice message from user {message.from_user.id}")
        
        # Download and transcribe voice
        logger.info("Downloading voice file...")
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_file.write(downloaded_file)
            temp_file_path = temp_file.name
        
        logger.info("Transcribing voice...")
        transcription = transcribe_voice(temp_file_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if transcription:
            logger.info(f"Voice transcribed: {transcription}")
            transcription_lower = transcription.lower()
            
            # Check for meal planning keywords
            if any(keyword in transcription_lower for keyword in ['plan', 'meal', 'food', 'diet']):
                # Extract number of days if mentioned
                days = 1
                import re
                day_match = re.search(r'(\d+)\s*day', transcription_lower)
                if day_match:
                    days = min(int(day_match.group(1)), 7)
                
                bot.reply_to(message, f"🎤 Heard: '{transcription}'\n🍽️ Generating {days}-day meal plan...")
                
                meal_plan_json = generate_meal_plan(days=days)
                if meal_plan_json:
                    # Save to local storage
                    user_id = str(message.from_user.id)
                    if user_id not in local_storage:
                        local_storage[user_id] = {}
                    local_storage[user_id]['meal_plan'] = meal_plan_json
                    
                    formatted_plan = format_meal_plan(meal_plan_json, days)
                    bot.reply_to(message, formatted_plan, parse_mode='HTML')
                    
                    # Generate shopping list
                    logger.info("Generating shopping list from voice command...")
                    shopping_items = extract_shopping_items(meal_plan_json)
                    if shopping_items:
                        logger.info(f"Shopping items received: {shopping_items}")
                        items_list = shopping_items.split('\n')
                        for item in items_list:
                            item = item.strip()
                            if item:
                                # Remove leading dash and space if present
                                if item.startswith('- '):
                                    item = item[2:]
                                elif item.startswith('-'):
                                    item = item[1:].strip()
                                
                                # Add to user's shopping list
                                if user_id not in local_storage:
                                    local_storage[user_id] = {}
                                if 'shopping_list' not in local_storage[user_id]:
                                    local_storage[user_id]['shopping_list'] = []
                                
                                if item not in local_storage[user_id]['shopping_list']:
                                    local_storage[user_id]['shopping_list'].append(item)
                                    logger.info(f"Added to shopping list: {item}")
                        
                        bot.reply_to(message, "🛒 Shopping list updated with meal plan ingredients!")
                    else:
                        logger.info("No shopping items received")
                        bot.reply_to(message, "⚠️ Could not generate shopping list from meal plan.")
                else:
                    bot.reply_to(message, "❌ Sorry, I couldn't generate a meal plan. Please try again.")
            else:
                bot.reply_to(message, f"🎤 I heard: '{transcription}'\n\n💡 Try saying 'plan meals' or 'create meal plan' to get started!")
        else:
            logger.info("Failed to transcribe voice")
            bot.reply_to(message, "❌ Sorry, I couldn't understand your voice message. Please try again.")
            
    except Exception as e:
        logger.error(f"Error transcribing voice: {e}")
        bot.reply_to(message, "❌ Sorry, there was an error processing your voice message. Please try again.")
    
    return "OK"

def handle_shopping_list(message):
    """Handle shopping list display"""
    user_id = str(message.from_user.id)
    
    if user_id in local_storage and 'shopping_list' in local_storage[user_id]:
        shopping_list = local_storage[user_id]['shopping_list']
        if shopping_list:
            list_text = "🛒 **Your Shopping List:**\n\n"
            for i, item in enumerate(shopping_list, 1):
                list_text += f"{i}. {item}\n"
            bot.reply_to(message, list_text, parse_mode='HTML')
        else:
            bot.reply_to(message, "🛒 Your shopping list is empty.\n\n💡 Generate a meal plan with `/planmeals` to add ingredients!")
    else:
        bot.reply_to(message, "🛒 Your shopping list is empty.\n\n💡 Generate a meal plan with `/planmeals` to add ingredients!")
    
    return "OK"

def handle_text_message(message):
    """Handle general text messages"""
    text = message.text.lower()
    
    if any(keyword in text for keyword in ['meal', 'food', 'plan', 'diet']):
        bot.reply_to(message, "🍽️ To generate a meal plan, use `/planmeals` or send a voice message saying 'plan meals'!")
    else:
        bot.reply_to(message, "💡 I'm here to help with your nutrition! Try:\n• `/planmeals` - Generate meal plans\n• `/shopping` - View shopping list\n• Send voice messages for hands-free operation")
    
    return "OK"

def lambda_handler(event, context):
    """
    AWS Lambda handler for Telegram webhook
    """
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # Parse the incoming webhook data
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event
            
        logger.info(f"Parsed webhook body: {body}")
        
        # Check if this is a Telegram webhook
        if 'message' in body:
            result = process_message(body['message'])
        elif 'callback_query' in body:
            # Handle callback queries if needed
            logger.info(f"Received callback query: {body['callback_query']}")
            result = "OK"
        else:
            logger.warning("No message or callback_query found in webhook")
            result = "OK"
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(f'Error: {str(e)}')
        } 