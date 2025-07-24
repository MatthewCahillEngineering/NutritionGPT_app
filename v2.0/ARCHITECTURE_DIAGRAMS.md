# NutritionGPT Coach v2.0 - Architecture Diagrams & Technical Details

## 🏗️ **System Architecture Overview**

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Telegram      │  │   Web App       │  │   Mobile App    │  │
│  │     Bot         │  │   (Future)      │  │   (Future)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Webhook       │  │   REST API      │  │   GraphQL       │  │
│  │   Endpoint      │  │   (Future)      │  │   (Future)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS LAMBDA                                │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              NUTRITION COACH CORE                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
│  │  │ Conversation│  │   User      │  │   Meal      │        │  │
│  │  │   Memory    │  │  Profiles   │  │  History    │        │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
│  │  │   AI Agent  │  │ Nutrition   │  │   Proactive │        │  │
│  │  │   Tools     │  │ Knowledge   │  │  Messaging  │        │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   OpenAI API    │  │   Vector DB     │  │   Storage       │  │
│  │   (GPT-4)       │  │   (Chroma)      │  │   (DynamoDB)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 **Data Flow Diagrams**

### **1. Message Processing Flow**
```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant A as API Gateway
    participant L as Lambda
    participant O as OpenAI
    participant M as Memory
    participant P as Profile

    U->>T: Send message
    T->>A: Webhook POST
    A->>L: Invoke Lambda
    L->>M: Get conversation memory
    L->>P: Get user profile
    L->>O: Call OpenAI API
    O->>L: Return AI response
    L->>M: Update memory
    L->>P: Update profile (if needed)
    L->>A: Return response
    A->>T: Send message to user
    T->>U: Display response
```

### **2. Conversation Memory Management**
```mermaid
graph TD
    A[New Message] --> B{User exists?}
    B -->|No| C[Create new memory]
    B -->|Yes| D[Load existing memory]
    C --> E[Add message to history]
    D --> E
    E --> F{History > 10 messages?}
    F -->|Yes| G[Keep last 10 messages]
    F -->|No| H[Keep all messages]
    G --> I[Update timestamp]
    H --> I
    I --> J[Store in memory]
    J --> K[Return for processing]
```

### **3. User Profile Creation Flow**
```mermaid
graph TD
    A[First interaction] --> B[Extract user info]
    B --> C[Create basic profile]
    C --> D[Ask for goals]
    D --> E[User provides goals]
    E --> F[Ask for measurements]
    F --> G[User provides measurements]
    G --> H[Calculate targets]
    H --> I[Ask for dietary restrictions]
    I --> J[User provides restrictions]
    J --> K[Complete profile]
    K --> L[Store profile]
    L --> M[Start coaching]
```

## 🧠 **AI Agent Architecture (LangChain Version)**

### **Agent System Overview**
```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Input     │───►│   Agent     │───►│   Output    │     │
│  │  Processor  │    │  Executor   │    │  Generator  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Memory    │    │   Tools     │    │   Response  │     │
│  │  Manager    │    │  Registry   │    │  Formatter  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Tool Execution Flow**
```mermaid
graph TD
    A[User Message] --> B[Agent Analysis]
    B --> C{Need Tool?}
    C -->|Yes| D[Select Tool]
    C -->|No| E[Direct Response]
    D --> F[Execute Tool]
    F --> G[Get Tool Result]
    G --> H[Format Result]
    H --> I[Generate Response]
    E --> I
    I --> J[Send to User]
```

## 📊 **Data Models & Relationships**

### **Entity Relationship Diagram**
```mermaid
erDiagram
    USER ||--o{ CONVERSATION_MEMORY : has
    USER ||--o{ MEAL_ENTRY : logs
    USER ||--o{ NUTRITION_PLAN : creates
    USER ||--o{ USER_PROFILE : has
    
    USER {
        string user_id PK
        string name
        datetime created_at
    }
    
    USER_PROFILE {
        string user_id FK
        int age
        float weight
        float height
        string activity_level
        list goals
        list dietary_restrictions
        int calorie_target
        float protein_target
    }
    
    CONVERSATION_MEMORY {
        string user_id FK
        list messages
        datetime last_interaction
    }
    
    MEAL_ENTRY {
        string user_id FK
        string meal_type
        list foods
        int total_calories
        float total_protein
        datetime timestamp
        string notes
    }
    
    NUTRITION_PLAN {
        string user_id FK
        string plan_type
        list meals
        int total_calories
        float total_protein
        datetime created_at
        string notes
    }
```

## 🔧 **Component Details**

### **1. Conversation Memory System**
```python
# Memory Structure
{
    "user_id": "12345",
    "messages": [
        {"role": "user", "content": "I want to build muscle"},
        {"role": "assistant", "content": "Great! Let's set up your profile..."},
        {"role": "user", "content": "I'm 180 lbs, 6'0\""},
        {"role": "assistant", "content": "Perfect! For muscle building..."}
    ],
    "last_interaction": "2025-07-24T10:30:00Z",
    "context": {
        "current_goal": "muscle_building",
        "profile_complete": False,
        "last_meal": "2 hours ago"
    }
}
```

### **2. User Profile Schema**
```python
# Profile Structure
{
    "user_id": "12345",
    "name": "John",
    "age": 25,
    "weight": 180.0,
    "height": 72.0,
    "activity_level": "moderate",
    "goals": ["build_muscle", "lose_fat"],
    "dietary_restrictions": ["vegetarian"],
    "calorie_target": 2200,
    "protein_target": 150.0,
    "preferences": {
        "meal_frequency": 4,
        "cooking_time": "30min",
        "budget": "medium"
    },
    "created_at": "2025-07-24T10:00:00Z",
    "updated_at": "2025-07-24T10:30:00Z"
}
```

### **3. Meal Entry Structure**
```python
# Meal Entry Structure
{
    "user_id": "12345",
    "meal_type": "lunch",
    "foods": [
        {"name": "grilled chicken", "calories": 180, "protein": 35},
        {"name": "brown rice", "calories": 110, "protein": 2},
        {"name": "broccoli", "calories": 30, "protein": 3}
    ],
    "total_calories": 320,
    "total_protein": 40,
    "timestamp": "2025-07-24T12:00:00Z",
    "notes": "Good protein content for muscle building"
}
```

## 🚀 **Deployment Architecture**

### **AWS Infrastructure**
```
┌─────────────────────────────────────────────────────────────┐
│                    AWS CLOUD                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   API       │    │   Lambda    │    │   CloudWatch│     │
│  │  Gateway    │◄──►│   Function  │◄──►│    Logs     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   DynamoDB  │    │   S3        │    │   IAM       │     │
│  │   (Future)  │    │   (Future)  │    │   Roles     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Lambda Function Structure**
```python
# Lambda Handler Flow
def lambda_handler(event, context):
    # 1. Extract Telegram update
    update = event
    
    # 2. Initialize bot
    bot = TelegramNutritionBot(telegram_token, openai_api_key)
    
    # 3. Process message
    result = bot.handle_message(update)
    
    # 4. Return response
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
```

## 📈 **Performance & Scaling**

### **Lambda Performance Metrics**
```
┌─────────────────────────────────────────────────────────────┐
│                    PERFORMANCE METRICS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Response Time:     < 3 seconds                             │
│  Memory Usage:      64-128 MB                               │
│  Cold Start:        ~500ms                                  │
│  Concurrent Users:  Limited by Lambda concurrency           │
│  Data Persistence:  In-memory (Lambda)                     │
│                                                             │
│  Scaling:           Automatic (AWS Lambda)                  │
│  Monitoring:        CloudWatch Logs & Metrics               │
│  Error Handling:    Graceful degradation                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Scaling Considerations**
```mermaid
graph TD
    A[Low Traffic] --> B[Single Lambda Instance]
    B --> C[In-memory Storage]
    C --> D[Fast Response]
    
    E[High Traffic] --> F[Multiple Lambda Instances]
    F --> G[Shared Storage Needed]
    G --> H[DynamoDB/RDS]
    H --> I[Session Management]
```

## 🔒 **Security & Privacy**

### **Security Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   API Key   │    │   IAM       │    │   Data      │     │
│  │  Encryption │    │   Roles     │    │  Encryption │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   HTTPS     │    │   VPC       │    │   Audit     │     │
│  │   TLS 1.3   │    │   (Future)  │    │   Logging   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 **Future Architecture Enhancements**

### **Phase 2: Persistent Storage**
```
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENT STORAGE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   DynamoDB  │    │   RDS       │    │   ElastiCache│    │
│  │   User Data │    │   Analytics │    │   Sessions  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Phase 3: Advanced AI Features**
```
┌─────────────────────────────────────────────────────────────┐
│                    ADVANCED AI STACK                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   LangChain │    │   Vector DB │    │   RAG       │     │
│  │   Agents    │    │   (Chroma)  │    │   System    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**This architecture provides a solid foundation for a scalable, conversational AI nutrition coach!** 🏗️🧠 