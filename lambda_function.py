import json
import os
import sys
from bot import NutritionBot
from database import NutritionDatabase

# Initialize bot instance
bot = NutritionBot()

def lambda_handler(event, context):
    """AWS Lambda handler for Telegram webhook"""
    try:
        # Parse the incoming webhook data
        body = json.loads(event['body'])
        
        # Process the update
        if 'message' in body:
            message = body['message']
            
            # Create a simple message object that mimics telebot's message structure
            class SimpleMessage:
                def __init__(self, data):
                    self.from_user = SimpleUser(data.get('from', {}))
                    self.text = data.get('text', '')
                    self.voice = data.get('voice')
                    self.message_id = data.get('message_id')
                
                def __str__(self):
                    return f"Message(text='{self.text}', from_user={self.from_user})"
            
            class SimpleUser:
                def __init__(self, data):
                    self.id = data.get('id')
                    self.first_name = data.get('first_name', '')
                    self.last_name = data.get('last_name', '')
                    self.username = data.get('username', '')
                
                def __str__(self):
                    return f"User(id={self.id}, name='{self.first_name}')"
            
            # Create message object
            msg = SimpleMessage(message)
            
            # Process the message based on content type
            if 'voice' in message:
                # Handle voice message
                bot.handle_voice_message(msg)
            elif 'text' in message:
                # Handle text message
                text = message['text']
                if text.startswith('/'):
                    # Handle commands
                    if text.startswith('/start') or text.startswith('/help'):
                        bot.send_welcome(msg)
                    elif text.startswith('/planmeals'):
                        bot.handle_meal_plan_command(msg)
                    elif text.startswith('/shopping'):
                        bot.handle_shopping_list(msg)
                    elif text.startswith('/addtolist'):
                        bot.handle_add_to_list(msg)
                    elif text.startswith('/removetolist'):
                        bot.handle_remove_from_list(msg)
                    elif text.startswith('/clear'):
                        bot.handle_clear_list(msg)
                    else:
                        bot.handle_text_message(msg)
                else:
                    bot.handle_text_message(msg)
        
        return {
            'statusCode': 200,
            'body': json.dumps('OK')
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

# For local testing
if __name__ == "__main__":
    # Simulate a webhook event
    test_event = {
        'body': json.dumps({
            'message': {
                'message_id': 1,
                'from': {
                    'id': 123456789,
                    'first_name': 'Test',
                    'username': 'testuser'
                },
                'text': '/start'
            }
        })
    }
    
    result = lambda_handler(test_event, None)
    print(result) 