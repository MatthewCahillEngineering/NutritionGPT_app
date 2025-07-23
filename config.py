import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'nutrition_tracker')

# Bot Settings
MAX_MEAL_PLAN_DAYS = 7
MAX_SHOPPING_LIST_ITEMS = 50

def load_config():
    """Load configuration from environment variables"""
    config = {
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN') or TELEGRAM_TOKEN,
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'aws_region': AWS_REGION,
        'dynamodb_table_name': DYNAMODB_TABLE_NAME,
        'max_meal_plan_days': MAX_MEAL_PLAN_DAYS,
        'max_shopping_list_items': MAX_SHOPPING_LIST_ITEMS
    }
    
    # Validate required environment variables
    missing_vars = []
    
    if not config['telegram_bot_token']:
        missing_vars.append('TELEGRAM_BOT_TOKEN')
    if not config['openai_api_key']:
        missing_vars.append('OPENAI_API_KEY')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return config

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    missing_vars = []
    
    if not TELEGRAM_TOKEN:
        missing_vars.append('TELEGRAM_TOKEN')
    if not OPENAI_API_KEY:
        missing_vars.append('OPENAI_API_KEY')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True 