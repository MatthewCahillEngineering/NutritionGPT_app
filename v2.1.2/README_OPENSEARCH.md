# NutritionGPT Coach v2.1.2 - OpenSearch Prototype

## 🚀 Advanced Memory System with Semantic Vector Search

This is a **prototype** of the next-generation nutrition coach that uses OpenSearch for semantic vector search and DynamoDB for structured user data. This represents the "understanding meaning" approach compared to v2.1's "remembering words" approach.

## 🧠 How v2.1.2 Works: "Understanding Meaning"

### **Semantic Vector Search**
```
User: "I'm sore from squats"
System: 
1. Generates embedding: [0.1, 0.3, -0.2, ...]
2. Searches for similar meaning vectors
3. Finds: "My legs hurt after deadlifts yesterday"
Result: "You mentioned muscle soreness after deadlifts yesterday - should we adjust your recovery?"
```

### **Advanced Memory Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Structured    │    │   Vector        │    │   Embedding     │
│   Memory        │    │   Memory        │    │   Generation    │
│                 │    │                 │    │                 │
│   DynamoDB      │    │   OpenSearch    │    │   OpenAI API    │
│   UserProfiles  │    │   KNN Search    │    │   text-embedding│
│   UserLogs      │    │   fitness_      │    │   -3-small      │
│                 │    │   memories      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🏗️ Architecture Components

### **1. OpenSearchMemoryManager**
- **Purpose**: Semantic vector search using KNN
- **Index**: `fitness_memories` with KNN mapping
- **Features**: 
  - Cosine similarity search
  - 1536-dimensional embeddings
  - User-scoped memory retrieval
  - Memory type filtering

### **2. DynamoDBUserManager**
- **Purpose**: Persistent structured data storage
- **Tables**:
  - `user_profiles`: User goals, preferences, stats
  - `user_logs`: All conversation history
- **Features**: 
  - Persistent user profiles (survives cold starts)
  - Complete interaction logging
  - Structured metadata storage

### **3. EmbeddingGenerator**
- **Purpose**: Convert text to semantic vectors
- **Model**: OpenAI `text-embedding-3-small`
- **Features**:
  - 1536-dimensional embeddings
  - Semantic understanding
  - Fallback to zero vectors on error

## 📊 Data Flow

### **Message Processing Pipeline**

1. **User sends message** → Lambda function triggered
2. **Load user profile** → From DynamoDB (persistent)
3. **Generate embedding** → Convert message to vector
4. **Semantic search** → Find similar past conversations
5. **Build rich context** → Combine profile + semantic memories
6. **Generate response** → Using OpenAI with deep context
7. **Store memories** → Save to both OpenSearch and DynamoDB

### **Memory Storage Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                    Dual Storage System                      │
├─────────────────────────────────────────────────────────────┤
│  OpenSearch (Vector Memory)        │  DynamoDB (Structured) │
│  ┌─────────────────────────────┐   │  ┌──────────────────┐  │
│  │ fitness_memories index      │   │  │ user_profiles    │  │
│  │ - text: conversation text   │   │  │ - goals          │  │
│  │ - embedding: [0.1, 0.3, ...]│   │  │ - weight        │  │
│  │ - memory_type: meal_log     │   │  │ - preferences   │  │
│  │ - metadata: rich context    │   │  │ - stats         │  │
│  └─────────────────────────────┘   │  └──────────────────┘  │
│                                    │  ┌──────────────────┐  │
│  Semantic Search:                  │  │ user_logs        │  │
│  - Find similar meanings           │  │ - input/output   │  │
│  - Relevance scoring               │  │ - timestamps     │  │
│  - Context awareness               │  │ - types          │  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Differences from v2.1

| Aspect | v2.1 (Current) | v2.1.2 (Prototype) |
|--------|---------------|-------------------|
| **Memory Type** | Keyword matching | Semantic vector search |
| **User Profiles** | Lost on cold start | Persistent in DynamoDB |
| **Relevance** | Word overlap | Meaning similarity |
| **Understanding** | "sore" = "sore" | "sore" ≈ "hurt" ≈ "pain" |
| **Context** | Recent conversations | Deep semantic context |
| **Scalability** | Limited by Lambda | Unlimited with OpenSearch |
| **Intelligence** | Basic pattern matching | Advanced semantic understanding |

## 🧠 Semantic Understanding Examples

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
4. Finds: "Feeling tired after heavy lifts"
5. Finds: "Muscle fatigue from compound movements"
Result: "You mentioned muscle soreness after deadlifts yesterday - should we adjust your recovery protocol?"
```

## 🔧 AWS Services Required

### **Manual Setup Required**

1. **OpenSearch Serverless**
   - Collection: `fitness-memory`
   - Index: `fitness_memories`
   - KNN plugin enabled
   - Vector search data access policy

2. **DynamoDB Tables**
   - `user_profiles`: User data (partition key: user_id)
   - `user_logs`: Conversation logs (partition key: user_id, sort key: timestamp)

3. **Lambda Function**
   - Runtime: Python 3.11
   - Memory: 1024 MB (increased for embeddings)
   - Timeout: 30 seconds
   - Environment variables: TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, OPENSEARCH_ENDPOINT

4. **IAM Permissions**
   - DynamoDB: Read/Write on both tables
   - OpenSearch: Access to collection
   - CloudWatch: Logging
   - Internet: OpenAI API access

## 💰 Cost Considerations

### **OpenSearch Serverless**
- **Free tier**: 750 hours/month
- **Beyond free tier**: ~$0.10/hour
- **Storage**: $0.10/GB/month
- **Data transfer**: $0.09/GB

### **Embedding Generation**
- **OpenAI text-embedding-3-small**: $0.00002/1K tokens
- **Typical message**: ~50 tokens = $0.000001 per message

### **Total Estimated Cost**
- **Low usage** (< 1000 messages/month): ~$5-10/month
- **Medium usage** (1000-10000 messages/month): ~$15-25/month
- **High usage** (> 10000 messages/month): ~$30-50/month

## 🚀 Advanced Features

### **Semantic Memory Types**
- **meal_log**: Food and nutrition conversations
- **goal_check**: Progress and goal-related discussions
- **advice**: Questions and recommendations
- **mood**: Energy levels and feelings
- **casual**: General conversation

### **Rich Context Building**
```
Context: User: John | Goals: lose weight, build muscle | Weight: 80kg
Semantic context:
- Memory: "You mentioned being tired after heavy lifts" (relevance: 0.85)
- Memory: "Your protein intake has been consistent" (relevance: 0.72)
- Memory: "You want to focus on compound movements" (relevance: 0.68)
```

### **Pattern Recognition**
- **Trends**: "You've been consistent with protein intake"
- **Progress**: "Your strength has improved over the last month"
- **Habits**: "You usually train on Monday, Wednesday, Friday"

## 🔍 Real-World Examples

### **What v2.1.2 Can Do:**

✅ **Semantic Understanding**
- "You mentioned muscle soreness after heavy lifts" (understands "sore" ≈ "hurt" ≈ "pain")
- "Based on your strength goals..." (persistent profile awareness)
- "You've been consistent with protein intake" (pattern recognition)

✅ **Deep Context**
- "Since you're focusing on compound movements, let's adjust your recovery"
- "Given your goal to lose weight while building muscle..."
- "Based on your previous experience with high-carb days..."

✅ **Intelligent Recommendations**
- "You mentioned being tired after deadlifts - should we adjust your recovery?"
- "Your protein intake has been good, but let's optimize timing"
- "Since you're training 3x/week, consider adding mobility work"

## 🛠️ Implementation Status

### **Current State: Prototype**
- ✅ Core architecture implemented
- ✅ OpenSearch integration
- ✅ DynamoDB user management
- ✅ Embedding generation
- ✅ Semantic search functionality
- ⚠️ Requires manual AWS setup
- ⚠️ Not yet deployed/tested

### **Next Steps**
1. **Manual AWS Setup**: Create OpenSearch collection and DynamoDB tables
2. **Deployment**: Deploy to Lambda with proper IAM permissions
3. **Testing**: Verify semantic search functionality
4. **Optimization**: Fine-tune embedding and search parameters

## 🎯 Migration Path

### **From v2.1 to v2.1.2**
1. **Deploy v2.1 first** - Get basic memory working
2. **Set up OpenSearch** - Create collection and index
3. **Migrate user data** - Move profiles to DynamoDB
4. **Deploy v2.1.2** - Switch to semantic search
5. **Gradual transition** - Run both versions in parallel

## 🔧 Configuration

### **Environment Variables**
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
OPENSEARCH_ENDPOINT=https://your-opensearch-domain.amazonaws.com
```

### **OpenSearch Index Mapping**
```json
{
  "settings": {
    "index": {
      "knn": true,
      "knn.space_type": "cosinesimil"
    }
  },
  "mappings": {
    "properties": {
      "user_id": {"type": "keyword"},
      "text": {"type": "text"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536
      },
      "memory_type": {"type": "keyword"},
      "timestamp": {"type": "date"},
      "metadata": {"type": "object"}
    }
  }
}
```

## 🎉 Benefits of v2.1.2

### **For Users**
- **Smarter conversations**: Bot understands meaning, not just words
- **Better memory**: Remembers context across conversations
- **Personalized advice**: Builds on deep understanding of goals
- **Natural interaction**: Feels like talking to a real coach

### **For Development**
- **Scalable architecture**: Can handle unlimited users
- **Rich data**: Complete conversation history and user profiles
- **Advanced analytics**: Pattern recognition and trend analysis
- **Future-proof**: Foundation for more advanced features

## 🚀 Conclusion

v2.1.2 represents the next evolution of the nutrition coach - from "remembering words" to "understanding meaning." While more complex to set up initially, it provides a foundation for truly intelligent, context-aware AI coaching that can understand users at a deep semantic level.

The prototype demonstrates the architecture and capabilities, ready for deployment once the AWS infrastructure is set up manually. 