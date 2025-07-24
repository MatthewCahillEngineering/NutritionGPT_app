# NutritionGPT v2.0 - Conversational AI Nutrition Coach

## 🧠 **Overview**

This is the **next generation** of NutritionGPT - a sophisticated conversational AI nutrition coach with memory, user profiles, and personalized guidance. This version transforms the simple meal planner into a true AI entity that learns and adapts.

## 📁 **Files**

### **Core AI Files**
- **`nutrition_coach_simple.py`** - Simplified conversational coach (Lambda-ready)
- **`nutrition_coach_v2.py`** - Full LangChain implementation (advanced)
- **`requirements_v2.txt`** - LangChain and AI dependencies

### **Deployment**
- **`deploy_conversational.py`** - v2.0 deployment script

### **Documentation**
- **`README_v2.md`** - Comprehensive v2.0 documentation
- **`ARCHITECTURE_DIAGRAMS.md`** - Technical diagrams and flowcharts
- **`CONVERSATION_EXAMPLES.md`** - Real conversation examples
- **`FEATURE_ROADMAP.md`** - Future development plan

## 🚀 **Deployment**

### **Deploy Simplified Version (Recommended)**
```bash
python deploy_conversational.py
```

### **Test Locally**
```python
from nutrition_coach_simple import NutritionCoach

coach = NutritionCoach(openai_api_key="your-key")
response = coach.process_message("test_user", "Hi! I want to build muscle.")
print(response)
```

## 🧠 **Features**

### **Conversational AI**
- 🧠 Conversation memory (10-message history)
- 👤 User profile management
- 📊 Meal logging and tracking
- 🎯 Personalized responses
- ⏰ Proactive coaching

### **Advanced Capabilities**
- Context-aware conversations
- Goal tracking and progress monitoring
- Nutrition knowledge base
- Adaptive recommendations
- Multi-session memory

## 📊 **Architecture**

```
User → Telegram → Lambda → Conversation Memory → User Profile → OpenAI → Response
```

- **Runtime**: Python 3.12
- **Memory**: 256 MB (increased for AI processing)
- **Timeout**: 30 seconds
- **Dependencies**: requests, openai (simple) / LangChain (advanced)

## 🎯 **Status**

- **Status**: 🔄 Development complete, ready for testing
- **Version**: Simplified conversational coach
- **Next**: Full LangChain implementation
- **Target**: Replace v1.0 in production

## 💬 **Example Conversations**

See `CONVERSATION_EXAMPLES.md` for detailed conversation flows including:
- New user onboarding
- Meal logging and tracking
- Progress monitoring
- Proactive coaching
- Problem solving

## 🏗️ **Technical Details**

See `ARCHITECTURE_DIAGRAMS.md` for:
- System architecture overview
- Data flow diagrams
- AI agent architecture
- Performance metrics
- Scaling considerations

## 🚀 **Next Steps**

1. **Test Simplified Version**: Deploy and test conversation memory
2. **Validate Features**: Test user profiles and meal logging
3. **Deploy LangChain Version**: Full AI agent capabilities
4. **Production Migration**: Replace v1.0 with v2.0

---

**v2.0** - The future of AI nutrition coaching! 🧠🎯 