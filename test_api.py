#!/usr/bin/env python3
import openai
import os

def test_openai_api():
    print("🔑 Testing OpenAI API...")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        # Test API connection
        client = openai.OpenAI(api_key=api_key)
        
        print("🧪 Testing GPT-3.5-turbo...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        print(f"✅ GPT Test successful: {response.choices[0].message.content}")
        
        # Test meal plan generation
        print("🧪 Testing meal plan generation...")
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
        
        meal_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutrition expert."},
                {"role": "user", "content": meal_prompt}
            ],
            max_tokens=500
        )
        
        print(f"✅ Meal plan test successful: {meal_response.choices[0].message.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API Test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api() 