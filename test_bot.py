#!/usr/bin/env python3
"""
Test script for NutritionGPT Bot
Tests all major functionality before deployment
"""

import os
import json
import sys
from unittest.mock import Mock, patch
from bot import NutritionBot
from database import NutritionDatabase
from ai_service import AIService

def test_database():
    """Test database operations"""
    print("🧪 Testing Database Operations...")
    
    try:
        db = NutritionDatabase()
        
        # Test shopping list operations
        test_user_id = 12345
        test_items = ["chicken breast", "eggs", "spinach"]
        
        # Save shopping list
        result = db.save_shopping_list(test_user_id, test_items)
        assert result == True, "Failed to save shopping list"
        print("  ✅ Save shopping list")
        
        # Get shopping list
        items = db.get_shopping_list(test_user_id)
        assert items == test_items, "Failed to retrieve shopping list"
        print("  ✅ Get shopping list")
        
        # Add item
        result = db.add_to_shopping_list(test_user_id, "avocado")
        assert result == True, "Failed to add item"
        print("  ✅ Add item to list")
        
        # Remove item
        result = db.remove_from_shopping_list(test_user_id, "eggs")
        assert result == True, "Failed to remove item"
        print("  ✅ Remove item from list")
        
        print("✅ Database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ai_service():
    """Test AI service operations"""
    print("🧪 Testing AI Service...")
    
    try:
        ai = AIService()
        
        # Test meal plan generation (mock OpenAI response)
        with patch.object(ai.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "days": [{
                    "day": 1,
                    "breakfast": {"name": "Protein Oatmeal", "ingredients": ["oats", "protein powder"], "protein": "25g", "calories": "300"},
                    "lunch": {"name": "Chicken Salad", "ingredients": ["chicken", "lettuce"], "protein": "30g", "calories": "400"},
                    "dinner": {"name": "Salmon", "ingredients": ["salmon", "broccoli"], "protein": "35g", "calories": "500"},
                    "snack": {"name": "Greek Yogurt", "ingredients": ["yogurt", "berries"], "protein": "20g", "calories": "200"}
                }]
            })
            mock_create.return_value = mock_response
            
            meal_plan = ai.generate_meal_plan(days=1)
            assert meal_plan is not None, "Failed to generate meal plan"
            print("  ✅ Generate meal plan")
        
        # Test shopping list extraction
        with patch.object(ai.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "- 2 lbs chicken breast\n- 1 dozen eggs\n- 1 lb spinach"
            mock_create.return_value = mock_response
            
            shopping_items = ai.extract_shopping_items("test meal plan")
            assert shopping_items is not None, "Failed to extract shopping items"
            print("  ✅ Extract shopping items")
        
        print("✅ AI Service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False

def test_bot_commands():
    """Test bot command handling"""
    print("🧪 Testing Bot Commands...")
    
    try:
        bot = NutritionBot()
        
        # Test welcome message
        mock_message = Mock()
        mock_message.from_user.id = 12345
        mock_message.text = "/start"
        
        # Mock bot reply method
        bot.bot.reply_to = Mock()
        
        # Test welcome handler
        bot.send_welcome(mock_message)
        assert bot.bot.reply_to.called, "Welcome message not sent"
        print("  ✅ Welcome message")
        
        # Test meal plan command
        mock_message.text = "/planmeals"
        bot.handle_meal_plan_command(mock_message)
        assert bot.bot.reply_to.called, "Meal plan command not handled"
        print("  ✅ Meal plan command")
        
        # Test shopping list command
        mock_message.text = "/shopping"
        bot.handle_shopping_list(mock_message)
        assert bot.bot.reply_to.called, "Shopping list command not handled"
        print("  ✅ Shopping list command")
        
        print("✅ Bot command tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bot command test failed: {e}")
        return False

def test_voice_processing():
    """Test voice message processing"""
    print("🧪 Testing Voice Processing...")
    
    try:
        bot = NutritionBot()
        
        # Mock voice message
        mock_message = Mock()
        mock_message.from_user.id = 12345
        mock_message.voice.file_id = "test_file_id"
        
        # Mock AI service methods
        bot.ai_service.download_voice_file = Mock(return_value="/tmp/test.ogg")
        bot.ai_service.transcribe_voice = Mock(return_value="plan meals for today")
        
        # Mock bot reply method
        bot.bot.reply_to = Mock()
        
        # Test voice message handling
        bot.handle_voice_message(mock_message)
        assert bot.bot.reply_to.called, "Voice message not processed"
        print("  ✅ Voice message processing")
        
        print("✅ Voice processing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Voice processing test failed: {e}")
        return False

def test_meal_plan_formatting():
    """Test meal plan formatting"""
    print("🧪 Testing Meal Plan Formatting...")
    
    try:
        bot = NutritionBot()
        
        # Test meal plan JSON
        test_meal_plan = {
            "days": [{
                "day": 1,
                "breakfast": {"name": "Protein Oatmeal", "protein": "25g", "calories": "300"},
                "lunch": {"name": "Chicken Salad", "protein": "30g", "calories": "400"},
                "dinner": {"name": "Salmon", "protein": "35g", "calories": "500"},
                "snack": {"name": "Greek Yogurt", "protein": "20g", "calories": "200"}
            }]
        }
        
        formatted = bot.format_meal_plan(json.dumps(test_meal_plan), 1)
        assert "Protein Oatmeal" in formatted, "Meal plan not formatted correctly"
        assert "25g" in formatted, "Protein info not included"
        print("  ✅ Meal plan formatting")
        
        print("✅ Meal plan formatting tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Meal plan formatting test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting NutritionGPT Bot Tests...\n")
    
    tests = [
        test_database,
        test_ai_service,
        test_bot_commands,
        test_voice_processing,
        test_meal_plan_formatting
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1) 