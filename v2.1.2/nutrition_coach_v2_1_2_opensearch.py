"""
NutritionGPT Coach v2.1.2 - OpenSearch Prototype
Advanced Memory System with Semantic Vector Search
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict
import numpy as np

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent

# AWS imports
import boto3
from botocore.exceptions import ClientError

# OpenSearch imports
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import NotFoundError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Data Models
@dataclass
class UserProfile:
    user_id: str
    name: str
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_restrictions: List[str] = None
    goals: List[str] = None
    calorie_target: Optional[int] = None
    protein_target: Optional[float] = None
    experience_level: str = "beginner"
    training_days: List[str] = None
    created_at: datetime = None
    last_interaction: datetime = None
    
    def __post_init__(self):
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.goals is None:
            self.goals = []
        if self.training_days is None:
            self.training_days = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_interaction is None:
            self.last_interaction = datetime.now()

@dataclass
class VectorMemory:
    user_id: str
    text: str
    embedding: List[float]
    memory_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class OpenSearchMemoryManager:
    """Advanced memory manager using OpenSearch for semantic vector search"""
    
    def __init__(self, opensearch_endpoint: str, opensearch_username: str = None, opensearch_password: str = None):
        self.opensearch_endpoint = opensearch_endpoint
        self.index_name = 'fitness_memories'
        
        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=[{'host': opensearch_endpoint.replace('https://', ''), 'port': 443}],
            http_auth=(opensearch_username, opensearch_password) if opensearch_username else None,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create OpenSearch index with KNN mapping if it doesn't exist"""
        try:
            # Check if index exists
            self.client.indices.get(index=self.index_name)
            logger.info(f"OpenSearch index {self.index_name} already exists")
        except NotFoundError:
            # Create index with KNN mapping
            index_mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.space_type": "cosinesimil"
                    }
                },
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "text": {"type": "text"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 1536  # OpenAI text-embedding-3-small dimension
                        },
                        "memory_type": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "metadata": {"type": "object"}
                    }
                }
            }
            
            self.client.indices.create(index=self.index_name, body=index_mapping)
            logger.info(f"Created OpenSearch index {self.index_name} with KNN mapping")
    
    def store_memory(self, user_id: str, text: str, embedding: List[float], memory_type: str = "general", metadata: Dict = None):
        """Store a memory with its embedding in OpenSearch"""
        try:
            document = {
                "user_id": user_id,
                "text": text,
                "embedding": embedding,
                "memory_type": memory_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            self.client.index(index=self.index_name, body=document)
            logger.info(f"Stored memory for user {user_id} in OpenSearch")
            
        except Exception as e:
            logger.error(f"Error storing memory in OpenSearch: {e}")
    
    def get_semantic_memories(self, user_id: str, query_embedding: List[float], k: int = 5, memory_type: str = None) -> List[Dict]:
        """Retrieve semantically similar memories using KNN search"""
        try:
            # Build query
            query = {
                "size": k,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding,
                                        "k": k
                                    }
                                }
                            },
                            {
                                "term": {
                                    "user_id": user_id
                                }
                            }
                        ]
                    }
                }
            }
            
            # Add memory type filter if specified
            if memory_type:
                query["query"]["bool"]["must"].append({
                    "term": {"memory_type": memory_type}
                })
            
            # Execute search
            response = self.client.search(index=self.index_name, body=query)
            
            # Extract results
            memories = []
            for hit in response['hits']['hits']:
                memories.append({
                    'text': hit['_source']['text'],
                    'memory_type': hit['_source']['memory_type'],
                    'timestamp': hit['_source']['timestamp'],
                    'metadata': hit['_source'].get('metadata', {}),
                    'score': hit['_score']
                })
            
            logger.info(f"Retrieved {len(memories)} semantic memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving semantic memories: {e}")
            return []

class DynamoDBUserManager:
    """Manages structured user data in DynamoDB"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.profiles_table_name = 'user_profiles'
        self.logs_table_name = 'user_logs'
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Create DynamoDB tables if they don't exist"""
        # Create UserProfiles table
        try:
            table = self.dynamodb.Table(self.profiles_table_name)
            table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                table = self.dynamodb.create_table(
                    TableName=self.profiles_table_name,
                    KeySchema=[{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'user_id', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST'
                )
                table.wait_until_exists()
                logger.info(f"Created DynamoDB table: {self.profiles_table_name}")
        
        # Create UserLogs table
        try:
            table = self.dynamodb.Table(self.logs_table_name)
            table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                table = self.dynamodb.create_table(
                    TableName=self.logs_table_name,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                table.wait_until_exists()
                logger.info(f"Created DynamoDB table: {self.logs_table_name}")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile from DynamoDB"""
        try:
            table = self.dynamodb.Table(self.profiles_table_name)
            response = table.get_item(Key={'user_id': user_id})
            
            if 'Item' in response:
                item = response['Item']
                return UserProfile(
                    user_id=item['user_id'],
                    name=item.get('name', 'User'),
                    age=item.get('age'),
                    weight=item.get('weight'),
                    height=item.get('height'),
                    activity_level=item.get('activity_level'),
                    dietary_restrictions=item.get('dietary_restrictions', []),
                    goals=item.get('goals', []),
                    calorie_target=item.get('calorie_target'),
                    protein_target=item.get('protein_target'),
                    experience_level=item.get('experience_level', 'beginner'),
                    training_days=item.get('training_days', []),
                    created_at=datetime.fromisoformat(item.get('created_at', datetime.now().isoformat())),
                    last_interaction=datetime.fromisoformat(item.get('last_interaction', datetime.now().isoformat()))
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def save_user_profile(self, profile: UserProfile):
        """Save user profile to DynamoDB"""
        try:
            table = self.dynamodb.Table(self.profiles_table_name)
            item = asdict(profile)
            item['created_at'] = profile.created_at.isoformat()
            item['last_interaction'] = profile.last_interaction.isoformat()
            
            table.put_item(Item=item)
            logger.info(f"Saved user profile for {profile.user_id}")
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
    
    def log_interaction(self, user_id: str, input_text: str, response: str, memory_type: str, metadata: Dict = None):
        """Log interaction to DynamoDB"""
        try:
            table = self.dynamodb.Table(self.logs_table_name)
            item = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'input': input_text,
                'response': response,
                'memory_type': memory_type,
                'metadata': json.dumps(metadata or {})
            }
            
            table.put_item(Item=item)
            logger.info(f"Logged interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

class EmbeddingGenerator:
    """Generates embeddings using OpenAI API"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

class NutritionCoachV2_1_2:
    def __init__(self, openai_api_key: str, telegram_token: str, opensearch_endpoint: str):
        self.openai_api_key = openai_api_key
        self.telegram_token = telegram_token
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.8,
            openai_api_key=openai_api_key
        )
        
        # Initialize advanced memory systems
        self.opensearch_memory = OpenSearchMemoryManager(opensearch_endpoint)
        self.user_manager = DynamoDBUserManager()
        self.embedding_generator = EmbeddingGenerator(openai_api_key)
        
        # Initialize conversation memory
        self.conversation_memories = {}  # user_id -> ConversationBufferWindowMemory
        
        # Initialize tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = [
            Tool(
                name="get_user_profile",
                func=self._get_user_profile,
                description="Get user's nutrition profile and goals"
            ),
            Tool(
                name="update_user_profile", 
                func=self._update_user_profile,
                description="Update user's profile information (goals, weight, etc.)"
            ),
            Tool(
                name="get_semantic_memories",
                func=self._get_semantic_memories,
                description="Get semantically relevant past conversations"
            ),
            Tool(
                name="get_nutrition_advice",
                func=self._get_nutrition_advice,
                description="Get personalized nutrition advice based on user's goals and history"
            )
        ]
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the AI agent with enhanced personality and semantic memory"""
        system_prompt = """You are Alex, a friendly and encouraging nutrition coach with advanced memory capabilities. You can understand the meaning behind conversations, not just words.

PERSONALITY:
- Keep responses short and conversational (1-3 sentences max)
- Use casual, friendly language - no formal nutrition jargon
- Be encouraging and positive, but honest
- Ask follow-up questions to keep the conversation flowing
- Reference past conversations with semantic understanding

CONVERSATION STYLE:
- "Hey! How's it going?" not "Hello, how may I assist you?"
- "That sounds delicious!" not "That meal provides good nutritional value"
- "You're doing great!" not "Your progress is satisfactory"
- Use emojis occasionally but not excessively

SEMANTIC MEMORY:
- Understand the meaning behind what users say
- Connect related concepts even if words don't match exactly
- Remember patterns and trends in their behavior
- Build on previous advice with deep context

TOOLS:
Use the available tools to:
- Access and update persistent user profiles
- Get semantically relevant past conversations
- Provide personalized advice based on deep context

Remember: You're a coach with a brain that understands meaning, not just words. Be human, be encouraging, be memorable, be smart."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _get_user_profile(self, user_id: str) -> str:
        """Get user's nutrition profile from DynamoDB"""
        profile = self.user_manager.get_user_profile(user_id)
        if profile:
            return f"User Profile: {asdict(profile)}"
        return "No profile found for this user."
    
    def _update_user_profile(self, user_id: str, **kwargs) -> str:
        """Update user's nutrition profile in DynamoDB"""
        profile = self.user_manager.get_user_profile(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id, name="User")
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.last_interaction = datetime.now()
        self.user_manager.save_user_profile(profile)
        return f"Updated profile for user {user_id}"
    
    def _get_semantic_memories(self, user_id: str, query: str, k: int = 5) -> str:
        """Get semantically relevant memories"""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Get semantic memories
            memories = self.opensearch_memory.get_semantic_memories(user_id, query_embedding, k)
            
            if memories:
                memory_texts = [f"Memory: {m['text']} (Type: {m['memory_type']})" for m in memories]
                return f"Relevant memories: {' | '.join(memory_texts)}"
            else:
                return "No relevant memories found."
                
        except Exception as e:
            logger.error(f"Error getting semantic memories: {e}")
            return "Error retrieving memories."
    
    def _get_nutrition_advice(self, user_id: str, topic: str = "general") -> str:
        """Get personalized nutrition advice"""
        profile = self.user_manager.get_user_profile(user_id)
        if not profile:
            return "I'd love to give you personalized advice! Tell me about your goals first."
        
        # Get recent semantic memories for context
        recent_memories = self._get_semantic_memories(user_id, f"nutrition advice {topic}", 3)
        
        advice_context = f"User: {profile.name}, Goals: {profile.goals}, Experience: {profile.experience_level}, Recent context: {recent_memories}"
        return f"Based on your profile and history: {advice_context}"
    
    def get_memory(self, user_id: str):
        """Get or create conversation memory for user"""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationBufferWindowMemory(
                k=20,
                return_messages=True
            )
        return self.conversation_memories[user_id]
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process a user message with advanced semantic memory"""
        try:
            # Get user profile from DynamoDB
            profile = self.user_manager.get_user_profile(user_id)
            
            # Generate embedding for current message
            message_embedding = self.embedding_generator.generate_embedding(message)
            
            # Get semantically relevant memories
            semantic_memories = self.opensearch_memory.get_semantic_memories(user_id, message_embedding, k=3)
            
            # Get conversation memory
            memory = self.get_memory(user_id)
            memory.chat_memory.add_user_message(message)
            chat_history = memory.chat_memory.messages
            
            # Create enhanced context with semantic understanding
            context_parts = []
            
            if profile:
                context_parts.append(f"User: {profile.name}")
                if profile.goals:
                    context_parts.append(f"Goals: {', '.join(profile.goals)}")
                if profile.weight:
                    context_parts.append(f"Weight: {profile.weight}kg")
            
            if semantic_memories:
                context_parts.append("Semantic context:")
                for mem in semantic_memories[:2]:
                    context_parts.append(f"- {mem['text']} (relevance: {mem['score']:.2f})")
            
            # Add context to the message
            enhanced_message = message
            if context_parts:
                enhanced_message = f"Context: {' | '.join(context_parts)}\n\nUser: {message}"
            
            # Run agent with enhanced context
            response = self.agent.invoke({
                "input": enhanced_message,
                "chat_history": chat_history
            })
            
            ai_response = response["output"]
            
            # Add AI response to memory
            memory.chat_memory.add_ai_message(ai_response)
            
            # Store in semantic memory
            memory_type = self._classify_message_type(message)
            full_text = f"User: {message}\nCoach: {ai_response}"
            
            self.opensearch_memory.store_memory(
                user_id=user_id,
                text=full_text,
                embedding=message_embedding,
                memory_type=memory_type,
                metadata={
                    "profile_goals": profile.goals if profile else [],
                    "profile_weight": profile.weight if profile else None,
                    "user_message": message,
                    "coach_response": ai_response
                }
            )
            
            # Log interaction to DynamoDB
            self.user_manager.log_interaction(
                user_id=user_id,
                input_text=message,
                response=ai_response,
                memory_type=memory_type,
                metadata={
                    "profile_goals": profile.goals if profile else [],
                    "profile_weight": profile.weight if profile else None
                }
            )
            
            # Update last interaction
            if profile:
                profile.last_interaction = datetime.now()
                self.user_manager.save_user_profile(profile)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Oops! Something went wrong. Can you try that again?"
    
    def _classify_message_type(self, message: str) -> str:
        """Classify message type for better memory organization"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["ate", "eat", "food", "meal", "breakfast", "lunch", "dinner"]):
            return "meal_log"
        elif any(word in message_lower for word in ["goal", "weight", "lose", "gain", "build"]):
            return "goal_check"
        elif any(word in message_lower for word in ["advice", "help", "what should", "recommend"]):
            return "advice"
        elif any(word in message_lower for word in ["feel", "mood", "tired", "energy", "good", "bad"]):
            return "mood"
        else:
            return "casual"

# Telegram Bot Integration
class TelegramNutritionBot:
    def __init__(self, telegram_token: str, openai_api_key: str, opensearch_endpoint: str):
        self.telegram_token = telegram_token
        self.coach = NutritionCoachV2_1_2(openai_api_key, telegram_token, opensearch_endpoint)
        self.base_url = f"https://api.telegram.org/bot{telegram_token}"
    
    def send_message(self, chat_id: str, text: str):
        """Send message via Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def handle_message(self, update: Dict) -> Dict:
        """Handle incoming Telegram message"""
        try:
            message = update.get("message", {})
            chat_id = str(message.get("chat", {}).get("id"))
            user_id = str(message.get("from", {}).get("id"))
            text = message.get("text", "")
            
            if not text:
                return {"status": "no_text"}
            
            # Process with advanced nutrition coach
            response = self.coach.process_message(user_id, text)
            
            # Send response
            self.send_message(chat_id, response)
            
            return {"status": "success", "response": response}
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {"status": "error", "error": str(e)}

# Lambda function handler
def lambda_handler(event, context):
    """AWS Lambda handler for Telegram webhook"""
    try:
        # Initialize bot
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        opensearch_endpoint = os.environ.get("OPENSEARCH_ENDPOINT")
        
        if not all([telegram_token, openai_api_key, opensearch_endpoint]):
            return {
                "statusCode": 500,
                "body": "Missing environment variables"
            }
        
        bot = TelegramNutritionBot(telegram_token, openai_api_key, opensearch_endpoint)
        
        # Parse Telegram update
        if "body" in event:
            update = json.loads(event["body"])
        else:
            update = event
        
        # Handle message
        result = bot.handle_message(update)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        } 