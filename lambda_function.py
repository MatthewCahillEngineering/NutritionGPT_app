import json
import os
import logging
from bot_fixed import NutritionGPTBot
from config import load_config

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize bot instance
config = load_config()
bot = NutritionGPTBot(config)

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
            
        # Handle Telegram webhook
        if 'message' in body:
            message = body['message']
            logger.info(f"Processing message: {message.get('text', 'Voice message')}")
            
            # Process the message using our bot
            bot.process_message(message)
            
        elif 'callback_query' in body:
            callback_query = body['callback_query']
            logger.info(f"Processing callback query: {callback_query}")
            
            # Handle callback queries if needed
            bot.process_callback_query(callback_query)
            
        return {
            'statusCode': 200,
            'body': json.dumps('OK')
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def set_webhook(event, context):
    """
    Set up Telegram webhook URL
    """
    try:
        webhook_url = event.get('webhook_url')
        if not webhook_url:
            return {
                'statusCode': 400,
                'body': json.dumps('webhook_url parameter required')
            }
            
        # Set webhook using bot instance
        success = bot.set_webhook(webhook_url)
        
        if success:
            return {
                'statusCode': 200,
                'body': json.dumps(f'Webhook set successfully to {webhook_url}')
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to set webhook')
            }
            
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        } 