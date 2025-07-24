#!/usr/bin/env python3
"""
Simple webhook handler for Telegram bot
"""
import json
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Webhook handler for Telegram bot
    """
    try:
        logger.info("Received webhook event: %s", json.dumps(event))
        
        # Parse the incoming webhook data
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event
            
        logger.info(f"Parsed webhook body: {body}")
        
        # For now, just return success
        # Later we'll add the actual bot logic here
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps('OK')
        }
        
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}")
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