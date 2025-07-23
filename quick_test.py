#!/usr/bin/env python3
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_meal_plan():
    print("🧪 Testing meal plan generation...")
    
    try:
        # Check if API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("💡 Set your API key in env_vars.txt or .env file")
            return False
            
        client = openai.OpenAI(api_key=api_key)
        
        # Test meal plan generation
        meal_prompt = """
        Create a 1-day meal plan with 3 meals (breakfast, lunch, dinner) and 1 snack.
        Focus on high protein, healthy meals.
        Format as JSON:
        {
            "days": [{
                "day": 1,
                "breakfast": {"name": "meal name", "protein": "XXg", "calories": "XXX"},
                "lunch": {"name": "meal name", "protein": "XXg", "calories": "XXX"},
                "dinner": {"name": "meal name", "protein": "XXg", "calories": "XXX"},
                "snack": {"name": "snack name", "protein": "XXg", "calories": "XXX"}
            }]
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutrition expert."},
                {"role": "user", "content": meal_prompt}
            ],
            max_tokens=500
        )
        
        print("✅ Meal plan generated successfully!")
        print(f"Response: {response.choices[0].message.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_meal_plan() 