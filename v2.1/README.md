# NutritionGPT Coach v2.1 🧠💬

**Enhanced Memory & Human-like Conversation**

## 🚀 What's New in v2.1

### 🧠 **Enhanced Memory System**
- **Vector-based Memory**: Uses ChromaDB for semantic memory storage
- **Context Awareness**: Remembers conversations, goals, and preferences
- **Smart Recall**: Retrieves relevant past interactions based on current context
- **Memory Classification**: Automatically categorizes conversations (meal_log, goal_check, advice, mood, casual)

### 💬 **Human-like Conversation**
- **Shorter Responses**: 1-3 sentences max (no more walls of text!)
- **Casual Language**: "Hey! How's it going?" instead of formal nutrition jargon
- **Encouraging Tone**: Positive, supportive, and motivating
- **Natural Flow**: References past conversations naturally
- **Personality**: "Alex" - your friendly nutrition coach friend

### 📊 **Improved User Profiles**
- **Enhanced Data Model**: More comprehensive user information
- **Experience Levels**: beginner, intermediate, advanced
- **Training Days**: Track workout schedules
- **Mood Tracking**: Capture emotional context with meals
- **Last Interaction**: Track engagement patterns

## 🛠️ Technical Improvements

### Memory Architecture
```python
# Vector-based memory storage
memory_manager.store_memory(
    user_id=user_id,
    message="I want to lose weight",
    response="Great goal! Let's start tracking your habits.",
    memory_type="goal_check"
)

# Semantic memory retrieval
relevant_memories = memory_manager.get_relevant_memories(
    user_id=user_id,
    query="How am I doing with my weight loss goal?",
    k=3
)
```

### Conversation Flow
```python
# Enhanced context injection
context_parts = [
    f"User: {profile.name}",
    f"Goals: {', '.join(profile.goals)}",
    f"Weight: {profile.weight}kg"
]

# Natural memory references
"Hey Alex! Remember when you mentioned wanting to build muscle? 
Your chicken and rice lunch was perfect for that goal! 🎯"
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd v2.1
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export OPENAI_API_KEY="your_openai_key"
export TELEGRAM_BOT_TOKEN="your_telegram_token"
```

### 3. Test Locally
```bash
python test_v2_1.py
```

### 4. Deploy to AWS Lambda
```bash
python deploy_v2_1.py
```

## 🧪 Testing the Improvements

### Memory Test
```python
# Test conversation flow
coach.process_message(user_id, "Hey! I'm new here")
coach.process_message(user_id, "My name is Alex, I want to build muscle")
coach.process_message(user_id, "I ate chicken and rice for lunch")
coach.process_message(user_id, "How am I doing with my muscle building goal?")
# Should reference previous info naturally
```

### Conversation Style Test
- ✅ "Hey! How's it going?"
- ❌ "Hello, how may I assist you?"
- ✅ "That sounds delicious!"
- ❌ "That meal provides good nutritional value"
- ✅ "You're doing great!"
- ❌ "Your progress is satisfactory"

## 📈 Key Features

### 🎯 **Smart Context Injection**
- Automatically includes relevant user profile info
- Retrieves semantically related past conversations
- Builds context for more personalized responses

### 🧠 **Memory Classification**
- **meal_log**: Food and nutrition tracking
- **goal_check**: Progress and goal discussions
- **advice**: Nutrition and fitness advice
- **mood**: Emotional state and energy levels
- **casual**: General conversation

### 💪 **Enhanced User Profiles**
```python
@dataclass
class UserProfile:
    user_id: str
    name: str
    goals: List[str]
    experience_level: str  # beginner, intermediate, advanced
    training_days: List[str]  # ["Mon", "Wed", "Fri"]
    last_interaction: datetime
    # ... more fields
```

## 🔧 Configuration

### Memory Settings
- **Vector Store**: ChromaDB (in-memory for Lambda compatibility)
- **Memory Window**: 20 recent messages
- **Relevant Memories**: Top 3 most similar past interactions
- **Memory Types**: 5 categories for better organization

### Conversation Settings
- **Temperature**: 0.8 (more natural responses)
- **Response Length**: 1-3 sentences max
- **Personality**: Friendly, encouraging, casual
- **Emojis**: Used occasionally but not excessively

## 🚀 Deployment

### AWS Lambda Configuration
- **Function Name**: `NutritionGPTBot-v2-1`
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 30 seconds
- **Handler**: `nutrition_coach_v2_1.lambda_handler`

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

## 🎯 Use Cases

### Perfect For:
- **Daily Nutrition Tracking**: Remember what you ate and when
- **Goal Progress**: Track progress toward fitness goals
- **Personalized Advice**: Get advice based on your history
- **Mood-based Coaching**: Adjust recommendations based on how you feel
- **Casual Check-ins**: Friendly conversation about nutrition

### Example Conversation Flow:
```
User: "Hey Alex!"
Bot: "Hey! How's it going? 😊"

User: "I'm feeling tired today"
Bot: "Sorry to hear that! Remember when you mentioned being stressed yesterday? 
Maybe we can find some energizing foods that work for you."

User: "What should I eat for dinner?"
Bot: "Since you're tired and trying to build muscle, how about something 
easy like grilled salmon with sweet potato? You loved that last week!"
```

## 🔮 Future Enhancements (v3.0)

- **Web Dashboard**: Visual progress tracking
- **Voice Integration**: ElevenLabs for voice responses
- **Avatar**: Visual companion interface
- **Proactive Reminders**: Smart notification system
- **Social Features**: Share progress with friends

## 🐛 Troubleshooting

### Common Issues:
1. **Memory not working**: Check ChromaDB initialization
2. **Long responses**: Verify system prompt is being used
3. **No context**: Ensure user profile is being created
4. **Lambda timeout**: Increase memory allocation

### Debug Mode:
```python
# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For issues or questions about v2.1:
- Check the test script for examples
- Verify environment variables are set
- Test memory functionality with the provided test cases

---

**v2.1 is all about making your nutrition coach feel like a real friend who remembers everything about you! 🎉** 