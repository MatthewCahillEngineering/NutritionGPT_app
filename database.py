import boto3
import json
from datetime import datetime, timedelta
from config import AWS_REGION, DYNAMODB_TABLE_NAME

class NutritionDatabase:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    def create_table_if_not_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            self.table.load()
        except:
            self.dynamodb.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'data_type', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'data_type', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            self.table.wait_until_exists()
    
    def save_meal_plan(self, user_id, meal_plan, days=1):
        """Save meal plan for user"""
        try:
            self.table.put_item(
                Item={
                    'user_id': str(user_id),
                    'data_type': f'meal_plan_{datetime.now().strftime("%Y%m%d")}',
                    'meal_plan': meal_plan,
                    'created_at': datetime.now().isoformat(),
                    'days': days
                }
            )
            return True
        except Exception as e:
            print(f"Error saving meal plan: {e}")
            return False
    
    def get_meal_plan(self, user_id, date=None):
        """Get meal plan for user"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        try:
            response = self.table.get_item(
                Key={
                    'user_id': str(user_id),
                    'data_type': f'meal_plan_{date}'
                }
            )
            return response.get('Item', {}).get('meal_plan')
        except Exception as e:
            print(f"Error getting meal plan: {e}")
            return None
    
    def save_shopping_list(self, user_id, items):
        """Save shopping list for user"""
        try:
            self.table.put_item(
                Item={
                    'user_id': str(user_id),
                    'data_type': 'shopping_list',
                    'items': items,
                    'updated_at': datetime.now().isoformat()
                }
            )
            return True
        except Exception as e:
            print(f"Error saving shopping list: {e}")
            return False
    
    def get_shopping_list(self, user_id):
        """Get shopping list for user"""
        try:
            response = self.table.get_item(
                Key={
                    'user_id': str(user_id),
                    'data_type': 'shopping_list'
                }
            )
            return response.get('Item', {}).get('items', [])
        except Exception as e:
            print(f"Error getting shopping list: {e}")
            return []
    
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