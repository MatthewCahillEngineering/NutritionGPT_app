import openai
import requests
import tempfile
import os
from config import OPENAI_API_KEY

class AIService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def transcribe_voice(self, voice_file_path):
        """Transcribe voice message using OpenAI Whisper"""
        try:
            with open(voice_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text.lower()
        except Exception as e:
            print(f"Error transcribing voice: {e}")
            return None
    
    def generate_meal_plan(self, user_preferences="", days=1):
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
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a nutrition expert and meal planner. Provide healthy, protein-rich meal plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating meal plan: {e}")
            return None
    
    def extract_shopping_items(self, meal_plan_text):
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
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts shopping list items from meal plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error extracting shopping items: {e}")
            return None
    
    def download_voice_file(self, file_id, bot_token):
        """Download voice file from Telegram"""
        try:
            # Get file info
            file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
            file_info = requests.get(file_info_url).json()
            
            if not file_info['ok']:
                return None
            
            file_path = file_info['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            
            # Download file
            response = requests.get(file_url)
            if response.status_code == 200:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
                temp_file.write(response.content)
                temp_file.close()
                return temp_file.name
            
            return None
        except Exception as e:
            print(f"Error downloading voice file: {e}")
            return None 