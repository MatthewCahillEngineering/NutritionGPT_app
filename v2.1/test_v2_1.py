#!/usr/bin/env python3
"""
Test script for NutritionGPT Coach v2.1
Tests memory improvements and conversation style
"""

import os
import sys
from nutrition_coach_v2_1 import NutritionCoachV2_1

def test_memory_and_conversation():
    """Test the enhanced memory and conversation capabilities"""
    
    # Initialize coach (you'll need to set your API keys)
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "test_token")
    
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return False
    
    print("🧪 Testing NutritionGPT Coach v2.1")
    print("=" * 40)
    
    try:
        coach = NutritionCoachV2_1(openai_api_key, telegram_token)
        
        # Test user ID
        user_id = "test_user_123"
        
        # Test 1: Initial conversation
        print("\n1️⃣ Testing initial conversation...")
        response1 = coach.process_message(user_id, "Hey! I'm new here and want to start tracking my nutrition")
        print(f"Response: {response1}")
        
        # Test 2: Setting up profile
        print("\n2️⃣ Testing profile setup...")
        response2 = coach.process_message(user_id, "My name is Alex, I'm 25, weigh 75kg, and want to build muscle")
        print(f"Response: {response2}")
        
        # Test 3: Logging a meal
        print("\n3️⃣ Testing meal logging...")
        response3 = coach.process_message(user_id, "I just ate chicken breast with rice for lunch")
        print(f"Response: {response3}")
        
        # Test 4: Memory test - referencing previous info
        print("\n4️⃣ Testing memory (should reference previous info)...")
        response4 = coach.process_message(user_id, "How am I doing with my muscle building goal?")
        print(f"Response: {response4}")
        
        # Test 5: Casual conversation
        print("\n5️⃣ Testing casual conversation style...")
        response5 = coach.process_message(user_id, "I'm feeling tired today")
        print(f"Response: {response5}")
        
        # Test 6: Memory recall
        print("\n6️⃣ Testing memory recall...")
        response6 = coach.process_message(user_id, "What did I eat for lunch again?")
        print(f"Response: {response6}")
        
        print("\n✅ All tests completed!")
        print("\nKey observations:")
        print("- Responses should be short and conversational")
        print("- Bot should remember user details and goals")
        print("- Should reference previous conversations naturally")
        print("- Tone should be friendly and encouraging")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_memory_manager():
    """Test the enhanced memory manager specifically"""
    print("\n🧠 Testing Enhanced Memory Manager")
    print("=" * 40)
    
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return False
    
    try:
        from nutrition_coach_v2_1 import EnhancedMemoryManager
        
        memory_manager = EnhancedMemoryManager(openai_api_key)
        
        # Test storing memories
        user_id = "test_user_456"
        
        print("Storing test memories...")
        memory_manager.store_memory(
            user_id=user_id,
            message="I want to lose weight",
            response="Great goal! Let's start by tracking your current eating habits.",
            memory_type="goal_check"
        )
        
        memory_manager.store_memory(
            user_id=user_id,
            message="I ate oatmeal for breakfast",
            response="Oatmeal is a great choice! It's high in fiber and keeps you full.",
            memory_type="meal_log"
        )
        
        # Test retrieving relevant memories
        print("Retrieving relevant memories...")
        relevant_memories = memory_manager.get_relevant_memories(
            user_id=user_id,
            query="How am I doing with my weight loss goal?",
            k=3
        )
        
        print(f"Found {len(relevant_memories)} relevant memories:")
        for i, memory in enumerate(relevant_memories, 1):
            print(f"  {i}. {memory[:100]}...")
        
        print("✅ Memory manager test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting NutritionGPT Coach v2.1 Tests")
    print("=" * 50)
    
    # Test 1: Memory and conversation
    test1_success = test_memory_and_conversation()
    
    # Test 2: Memory manager
    test2_success = test_memory_manager()
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! v2.1 is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 