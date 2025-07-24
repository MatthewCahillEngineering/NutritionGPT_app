#!/usr/bin/env python3
"""
Simplified Lambda Function for NutritionGPT Bot
This version avoids pydantic dependencies
"""

import json
import os
import requests
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Get environment variables
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        if not bot_token or not openai_key:
            logger.error("Missing environment variables")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Missing environment variables'})
            }
        
        # Handle the event structure from API Gateway
        telegram_update = None
        
        # Check if event is already a Telegram update (direct invocation)
        if 'update_id' in event and 'message' in event:
            telegram_update = event
            logger.info("Direct Telegram update detected")
        
        # Check if event has body (API Gateway)
        elif 'body' in event:
            body = event.get('body', '{}')
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in body")
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Invalid JSON'})
                    }
            
            if 'update_id' in body and 'message' in body:
                telegram_update = body
                logger.info("Telegram update from API Gateway detected")
        
        # Process the Telegram update
        if telegram_update:
            logger.info("Processing Telegram update")
            return handle_telegram_update(telegram_update, bot_token, openai_key)
        else:
            logger.info("Not a valid Telegram update")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Not a valid Telegram update'})
            }
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_telegram_update(update, bot_token, openai_key):
    """Handle Telegram update"""
    try:
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        if not chat_id:
            logger.error("No chat_id found")
            return {'statusCode': 200, 'body': 'OK'}
        
        logger.info(f"Processing message: {text} from chat_id: {chat_id}")
        
        # Handle different commands
        if text == '/start':
            response_text = "🤖 Welcome to NutritionGPT Bot!\n\nI can help you with:\n• /planmeals - Generate meal plans\n• /shopping - Create shopping lists\n\nJust send me a message or use the commands above!"
        
        elif text == '/planmeals':
            response_text = generate_meal_plan(openai_key)
        
        elif text == '/shopping':
            response_text = "🛒 Shopping list feature coming soon! For now, try /planmeals to get meal suggestions."
        
        elif text.lower() in ['plan meals', 'meal plan', 'plan my meals']:
            response_text = generate_meal_plan(openai_key)
        
        else:
            response_text = "I'm here to help with nutrition! Try:\n• /planmeals - Get meal suggestions\n• /shopping - Create shopping lists"
        
        # Send response to Telegram
        send_telegram_message(bot_token, chat_id, response_text)
        
        return {'statusCode': 200, 'body': 'OK'}
        
    except Exception as e:
        logger.error(f"Error handling Telegram update: {str(e)}")
        return {'statusCode': 200, 'body': 'OK'}

def generate_meal_plan(openai_key):
    """Generate a simple meal plan using OpenAI"""
    try:
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful nutrition assistant. Provide simple, healthy meal suggestions.'
                },
                {
                    'role': 'user',
                    'content': 'Give me a simple 3-day meal plan with breakfast, lunch, and dinner. Keep it healthy and easy to prepare.'
                }
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            meal_plan = result['choices'][0]['message']['content']
            return f"🍽️ Here's your meal plan:\n\n{meal_plan}"
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return "Sorry, I couldn't generate a meal plan right now. Please try again later."
            
    except Exception as e:
        logger.error(f"Error generating meal plan: {str(e)}")
        return "Sorry, I encountered an error generating your meal plan. Please try again."

def send_telegram_message(bot_token, chat_id, text):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
        else:
            logger.info(f"Message sent successfully to chat_id: {chat_id}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")

def test_function():
    """Test function for local development"""
    test_event = {
        'body': json.dumps({
            'update_id': 123456789,
            'message': {
                'message_id': 1,
                'from': {'id': 123456789, 'first_name': 'Test'},
                'chat': {'id': 123456789, 'type': 'private'},
                'date': 1234567890,
                'text': '/start'
            }
        })
    }
    
    # Set test environment variables
    os.environ['TELEGRAM_BOT_TOKEN'] = 'your_test_token'
    os.environ['OPENAI_API_KEY'] = 'your_test_key'
    
    result = lambda_handler(test_event, None)
    print(f"Test result: {result}")

if __name__ == "__main__":
    test_function() 