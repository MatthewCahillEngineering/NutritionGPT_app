#!/usr/bin/env python3
from ai_service import AIService

def test_ai_service():
    print("🧪 Testing AI Service...")
    
    try:
        ai = AIService()
        
        # Test meal plan generation
        print("Testing meal plan generation...")
        meal_plan = ai.generate_meal_plan(days=1)
        
        if meal_plan:
            print("✅ Meal plan generated successfully!")
            print(f"Response: {meal_plan[:200]}...")
            
            # Test shopping list extraction
            print("\nTesting shopping list extraction...")
            shopping_items = ai.extract_shopping_items(meal_plan)
            
            if shopping_items:
                print("✅ Shopping list extracted successfully!")
                print(f"Shopping items: {shopping_items[:200]}...")
            else:
                print("❌ Failed to extract shopping items")
        else:
            print("❌ Failed to generate meal plan")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_service() 