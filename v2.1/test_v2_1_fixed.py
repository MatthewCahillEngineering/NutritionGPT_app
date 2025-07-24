#!/usr/bin/env python3
"""
Test script for NutritionGPT Coach v2.1 Fixed
Tests the core functionality without requiring AWS services
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path to import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_memory_manager():
    """Test the memory manager functionality"""
    print("🧪 Testing Memory Manager...")
    
    try:
        from nutrition_coach_v2_1_fixed import LambdaCompatibleMemoryManager
        
        # Test with in-memory only (no AWS)
        memory_manager = LambdaCompatibleMemoryManager(use_dynamodb=False)
        
        # Test storing memory
        memory_manager.store_memory(
            user_id="test_user",
            message="I ate chicken for lunch",
            response="That's great! Chicken is a good protein source.",
            memory_type="meal_log"
        )
        
        # Test retrieving memories
        memories = memory_manager.get_relevant_memories(
            user_id="test_user",
            query="chicken lunch",
            k=3
        )
        
        print(f"✅ Memory manager test passed. Retrieved {len(memories)} memories.")
        return True
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        return False

def test_nutrition_coach():
    """Test the nutrition coach functionality"""
    print("🧪 Testing Nutrition Coach...")
    
    try:
        from nutrition_coach_v2_1_fixed import NutritionCoachV2_1
        
        # Test with mock API keys
        coach = NutritionCoachV2_1(
            openai_api_key="test_key",
            telegram_token="test_token"
        )
        
        # Test message processing (should handle missing API keys gracefully)
        try:
            response = coach.process_message("test_user", "Hello!")
            print(f"✅ Coach initialization test passed.")
        except Exception as e:
            if "API key" in str(e) or "authentication" in str(e).lower():
                print("✅ Coach initialization test passed (expected API error).")
            else:
                print(f"❌ Coach test failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Nutrition coach test failed: {e}")
        return False

def test_data_models():
    """Test the data models"""
    print("🧪 Testing Data Models...")
    
    try:
        from nutrition_coach_v2_1_fixed import UserProfile, MealEntry, ConversationMemory
        
        # Test UserProfile
        profile = UserProfile(
            user_id="test_user",
            name="Test User",
            weight=70.0,
            goals=["lose weight", "build muscle"]
        )
        
        assert profile.user_id == "test_user"
        assert profile.weight == 70.0
        assert "lose weight" in profile.goals
        
        # Test MealEntry
        meal = MealEntry(
            user_id="test_user",
            meal_type="lunch",
            foods=[{"name": "chicken", "calories": 200, "protein": 25}],
            total_calories=200,
            total_protein=25,
            timestamp=datetime.now()
        )
        
        assert meal.meal_type == "lunch"
        assert meal.total_calories == 200
        
        # Test ConversationMemory
        memory = ConversationMemory(
            user_id="test_user",
            message="Hello",
            response="Hi there!",
            timestamp=datetime.now(),
            memory_type="casual"
        )
        
        assert memory.memory_type == "casual"
        
        print("✅ Data models test passed.")
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        return False

def test_message_classification():
    """Test message type classification"""
    print("🧪 Testing Message Classification...")
    
    try:
        from nutrition_coach_v2_1_fixed import NutritionCoachV2_1
        
        coach = NutritionCoachV2_1(
            openai_api_key="test_key",
            telegram_token="test_token"
        )
        
        # Test different message types
        test_cases = [
            ("I ate chicken for lunch", "meal_log"),
            ("I want to lose weight", "goal_check"),
            ("What should I eat?", "advice"),
            ("I feel tired today", "mood"),
            ("Hello there", "casual")
        ]
        
        for message, expected_type in test_cases:
            classified_type = coach._classify_message_type(message)
            if classified_type == expected_type:
                print(f"✅ '{message}' correctly classified as {classified_type}")
            else:
                print(f"❌ '{message}' classified as {classified_type}, expected {expected_type}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Message classification test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting NutritionGPT Coach v2.1 Fixed Tests")
    print("=" * 50)
    
    tests = [
        test_data_models,
        test_memory_manager,
        test_nutrition_coach,
        test_message_classification
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixed version is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 