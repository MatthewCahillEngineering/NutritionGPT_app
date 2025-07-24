# NutritionGPT Coach v2.1 - Architecture & Design

## 🏗️ Current Architecture Overview

This document explains how the v2.1 fixed version works, its architecture, and how it compares to the planned v2.1.2 OpenSearch version.

## 🧠 Current v2.1 Memory System

### **How It Works: "Remembering Words"**

The current v2.1 uses a **keyword-based memory system** that searches for exact word matches in past conversations.

```
User: "I'm sore from squats"
System: Searches for conversations containing "sore" or "squats"
Result: "You mentioned being sore last week too"
```

### **Memory Storage Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Primary       │    │   Backup        │    │   Fallback      │
│   DynamoDB      │    │   S3 Bucket     │    │   In-Memory     │
│                 │    │                 │    │   (Temporary)   │
│ nutrition_      │    │ nutrition-      │    │ Lambda Memory   │
│ memories table  │    │ memories-bucket │    │ (Lost on cold   │
│                 │    │                 │    │  start)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow**

1. **User sends message** → Lambda function triggered
2. **Load user profile** → From Lambda memory (temporary)
3. **Search past memories** → Query DynamoDB for relevant conversations
4. **Keyword matching** → Find conversations with matching words
5. **Build context** → Combine user profile + relevant memories
6. **Generate response** → Using OpenAI with enhanced context
7. **Store new memory** → Save to DynamoDB for future reference

### **Memory Types Classification**

The system automatically classifies messages into types:

- `meal_log`: Food and meal-related messages
- `goal_check`: Weight, goals, progress updates  
- `advice`: Questions asking for help/recommendations
- `mood`: How user is feeling, energy levels
- `casual`: General conversation

## 📊 Data Models

### **UserProfile** (In-Memory, Temporary)
```python
@dataclass
class UserProfile:
    user_id: str
    name: str
    weight: Optional[float] = None
    goals: List[str] = None
    experience_level: str = "beginner"
    training_days: List[str] = None
    # ... other fields
```

### **ConversationMemory** (Persistent in DynamoDB)
```python
@dataclass
class ConversationMemory:
    user_id: str
    message: str
    response: str
    timestamp: datetime
    memory_type: str  # meal_log, goal_check, etc.
    metadata: Dict[str, Any] = None
```

### **DynamoDB Table Schema**
```
Table: nutrition_memories
├── Partition Key: user_id (String)
├── Sort Key: timestamp (String)
├── Attributes:
│   ├── message (String)
│   ├── response (String)
│   ├── memory_type (String)
│   └── metadata (String - JSON)
```

## 🔍 Relevance Scoring

### **Current Method: Keyword Matching**
```python
# Simple word overlap scoring
query_words = set("I'm sore from squats".lower().split())
# query_words = {"i'm", "sore", "from", "squats"}

for memory in past_conversations:
    memory_text = f"{memory.message} {memory.response}".lower()
    matches = sum(1 for word in query_words if word in memory_text)
    # Score based on number of matching words
```

### **Example Matching**
```
Current Query: "I'm sore from squats"
Past Memory: "My legs hurt after deadlifts yesterday"
Matches: 0 (no word overlap)

Past Memory: "I'm feeling sore today"
Matches: 2 ("i'm", "sore")

Past Memory: "Squats are tough"
Matches: 1 ("squats")
```

## 🎯 Real-World Examples

### **What v2.1 Can Do Well:**
- ✅ "You ate chicken yesterday" (exact word match)
- ✅ "You want to lose weight" (keyword found)
- ✅ "You mentioned being sore last week" (word overlap)
- ✅ Remember recent conversation context

### **What v2.1 Can't Do:**
- ❌ "You mentioned muscle soreness after heavy lifts" (semantic understanding)
- ❌ "Based on your strength goals..." (persistent profile lost on cold start)
- ❌ "You've been consistent with protein intake" (pattern recognition)

## 🚀 Performance Characteristics

### **Response Times**
- **Cold start**: 2-5 seconds (Lambda initialization)
- **Warm start**: 500ms-1 second
- **Memory retrieval**: 100-300ms (DynamoDB query)

### **Memory Usage**
- **Base memory**: ~200MB
- **With dependencies**: ~400MB
- **Peak usage**: ~450MB

### **Cost**
- **Lambda**: Free tier + ~$0.20 per million requests
- **DynamoDB**: Pay-per-request, ~$1.25 per million reads
- **Total**: Very low cost for personal use

## 🔄 Comparison: v2.1 vs v2.1.2 (Planned)

| Aspect | Current v2.1 | Planned v2.1.2 |
|--------|-------------|----------------|
| **Memory Type** | Keyword matching | Semantic vector search |
| **User Profiles** | Lost on cold start | Persistent in DynamoDB |
| **Relevance** | Word overlap | Meaning similarity |
| **Scalability** | Limited by Lambda memory | Unlimited with OpenSearch |
| **Intelligence** | Basic context | Advanced semantic understanding |
| **Cost** | Very low | Low-medium (OpenSearch) |
| **Complexity** | Simple | More sophisticated |

## 🧠 How They Work Differently

### **v2.1 - "Remembering Words"**
```
User: "I'm sore from squats"
System: Searches for conversations containing "sore" or "squats"
Result: "You mentioned being sore last week too"
```

### **v2.1.2 - "Understanding Meaning"**
```
User: "I'm sore from squats"
System: 
1. Generates embedding: [0.1, 0.3, -0.2, ...]
2. Searches for similar meaning vectors
3. Finds: "My legs hurt after deadlifts yesterday"
Result: "You mentioned muscle soreness after deadlifts yesterday - should we adjust your recovery?"
```

## 🎯 Migration Path

### **Phase 1: Deploy v2.1** ✅
- Get basic memory working
- Test Lambda deployment
- Understand the flow
- **Status**: Ready to deploy

### **Phase 2: Add OpenSearch** (v2.1.2)
- Keep current DynamoDB setup
- Add OpenSearch for vector search
- Gradually migrate to semantic search

### **Phase 3: Full AWS-native** (Future)
- Separate user profiles to DynamoDB
- Use OpenSearch for all memory
- Add embedding generation

## 🔧 Current Limitations & Trade-offs

### **Limitations**
1. **User profiles lost on cold start** - Need to rebuild each time
2. **Basic keyword matching** - No semantic understanding
3. **Limited context window** - Only recent conversations
4. **No pattern recognition** - Can't identify trends

### **Trade-offs**
- **Simplicity vs Intelligence**: Current version is simple but functional
- **Cost vs Features**: Very low cost but basic capabilities
- **Deployment vs Development**: Easy to deploy, harder to enhance

## 🎉 Why v2.1 is Still Great

Despite limitations, v2.1 provides:
- ✅ **Persistent conversation memory** across Lambda invocations
- ✅ **User context awareness** during conversations
- ✅ **Lambda compatibility** with graceful fallbacks
- ✅ **Low cost** and simple maintenance
- ✅ **Easy to upgrade** to v2.1.2 later

## 🚀 Next Steps

1. **Deploy v2.1** - Get the basic memory system working
2. **Test thoroughly** - Ensure it feels "sticky and smart"
3. **Gather feedback** - See how users interact with it
4. **Plan v2.1.2** - Add OpenSearch for semantic understanding

The current v2.1 is a solid foundation that will already feel much more intelligent than v2.0, and provides a clear upgrade path to the more sophisticated v2.1.2 system. 