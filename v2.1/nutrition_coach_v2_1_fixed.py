"""
NutritionGPT Coach v2.1 - Fixed for AWS Lambda
Enhanced Memory & Human-like Conversation with Lambda-compatible storage
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict
import hashlib
import pickle
import base64

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
    experience_level: str = "beginner"  # beginner, intermediate, advanced
    training_days: List[str] = None  # ["Mon", "Wed", "Fri"]
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
class MealEntry:
    user_id: str
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[Dict[str, Any]]  # [{"name": "chicken", "calories": 200, "protein": 25}]
    total_calories: int
    total_protein: float
    timestamp: datetime
    notes: Optional[str] = None
    mood: Optional[str] = None  # "good", "tired", "stressed", etc.

@dataclass
class ConversationMemory:
    user_id: str
    message: str
    response: str
    timestamp: datetime
    memory_type: str  # "meal_log", "goal_check", "advice", "casual", "mood"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class LambdaCompatibleMemoryManager:
    """Memory manager compatible with AWS Lambda using DynamoDB or S3"""
    
    def __init__(self, use_dynamodb: bool = True):
        self.use_dynamodb = use_dynamodb
        self.dynamodb = None
        self.s3 = None
        
        if use_dynamodb:
            try:
                self.dynamodb = boto3.resource('dynamodb')
                self.table_name = 'nutrition_memories'
                self._ensure_table_exists()
            except Exception as e:
                logger.warning(f"DynamoDB not available, falling back to S3: {e}")
                self.use_dynamodb = False
        
        if not self.use_dynamodb:
            try:
                self.s3 = boto3.client('s3')
                self.bucket_name = 'nutrition-memories-bucket'
            except Exception as e:
                logger.warning(f"S3 not available, using in-memory only: {e}")
    
    def _ensure_table_exists(self):
        """Ensure DynamoDB table exists"""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
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
                logger.info(f"Created DynamoDB table: {self.table_name}")
    
    def store_memory(self, user_id: str, message: str, response: str, memory_type: str = "general", metadata: Dict = None):
        """Store a conversation memory"""
        try:
            memory = ConversationMemory(
                user_id=user_id,
                message=message,
                response=response,
                timestamp=datetime.now(),
                memory_type=memory_type,
                metadata=metadata or {}
            )
            
            if self.use_dynamodb and self.dynamodb:
                # Store in DynamoDB
                table = self.dynamodb.Table(self.table_name)
                item = {
                    'user_id': user_id,
                    'timestamp': memory.timestamp.isoformat(),
                    'message': message,
                    'response': response,
                    'memory_type': memory_type,
                    'metadata': json.dumps(metadata or {})
                }
                table.put_item(Item=item)
                
            elif self.s3:
                # Store in S3
                key = f"memories/{user_id}/{memory.timestamp.isoformat()}.json"
                data = asdict(memory)
                data['timestamp'] = memory.timestamp.isoformat()
                self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=json.dumps(data)
                )
            
            logger.info(f"Stored memory for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
    
    def get_relevant_memories(self, user_id: str, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant memories using simple keyword matching"""
        try:
            memories = []
            
            if self.use_dynamodb and self.dynamodb:
                # Get from DynamoDB
                table = self.dynamodb.Table(self.table_name)
                response = table.query(
                    KeyConditionExpression='user_id = :uid',
                    ExpressionAttributeValues={':uid': user_id},
                    ScanIndexForward=False,  # Most recent first
                    Limit=k * 2  # Get more to filter
                )
                
                items = response.get('Items', [])
                
            elif self.s3:
                # Get from S3
                try:
                    response = self.s3.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=f"memories/{user_id}/"
                    )
                    items = []
                    for obj in response.get('Contents', [])[:k * 2]:
                        obj_response = self.s3.get_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        item = json.loads(obj_response['Body'].read())
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error reading from S3: {e}")
                    items = []
            else:
                items = []
            
            # Simple relevance scoring based on keyword matching
            query_words = set(query.lower().split())
            scored_memories = []
            
            for item in items:
                message = item.get('message', '')
                response = item.get('response', '')
                combined_text = f"{message} {response}".lower()
                
                # Count matching words
                matches = sum(1 for word in query_words if word in combined_text)
                if matches > 0:
                    scored_memories.append((matches, f"User: {message}\nCoach: {response}"))
            
            # Sort by relevance and return top k
            scored_memories.sort(reverse=True)
            memories = [memory for score, memory in scored_memories[:k]]
            
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

class NutritionCoachV2_1:
    def __init__(self, openai_api_key: str, telegram_token: str):
        self.openai_api_key = openai_api_key
        self.telegram_token = telegram_token
        
        # Initialize OpenAI with better temperature for human-like responses
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.8,  # Slightly higher for more natural responses
            openai_api_key=openai_api_key
        )
        
        # Initialize enhanced memory system
        self.memory_manager = LambdaCompatibleMemoryManager(use_dynamodb=True)
        self.conversation_memories = {}  # user_id -> ConversationBufferWindowMemory
        self.user_profiles = {}  # user_id -> UserProfile
        self.meal_history = {}  # user_id -> List[MealEntry]
        
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
                name="log_meal",
                func=self._log_meal,
                description="Log a meal with foods, calories, and protein"
            ),
            Tool(
                name="get_meal_history",
                func=self._get_meal_history,
                description="Get user's recent meal history and nutrition summary"
            ),
            Tool(
                name="get_nutrition_advice",
                func=self._get_nutrition_advice,
                description="Get personalized nutrition advice based on user's goals and history"
            )
        ]
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the AI agent with enhanced personality and memory"""
        system_prompt = """You are Alex, a friendly and encouraging nutrition coach. You're like a supportive friend who happens to be a nutrition expert.

PERSONALITY:
- Keep responses short and conversational (1-3 sentences max)
- Use casual, friendly language - no formal nutrition jargon
- Be encouraging and positive, but honest
- Ask follow-up questions to keep the conversation flowing
- Remember details about the user and reference them naturally

CONVERSATION STYLE:
- "Hey! How's it going?" not "Hello, how may I assist you?"
- "That sounds delicious!" not "That meal provides good nutritional value"
- "You're doing great!" not "Your progress is satisfactory"
- Use emojis occasionally but not excessively

MEMORY:
- Always reference past conversations naturally
- Remember their goals, preferences, and recent meals
- Build on previous advice given

TOOLS:
Use the available tools to:
- Access and update user profiles
- Log meals and track nutrition
- Get meal history for context
- Provide personalized advice

Remember: You're a coach, not a textbook. Be human, be encouraging, be memorable."""

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
        """Get user's nutrition profile"""
        profile = self.user_profiles.get(user_id)
        if profile:
            return f"User Profile: {asdict(profile)}"
        return "No profile found for this user."
    
    def _update_user_profile(self, user_id: str, **kwargs) -> str:
        """Update user's nutrition profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id, name="User")
        
        profile = self.user_profiles[user_id]
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.last_interaction = datetime.now()
        return f"Updated profile for user {user_id}"
    
    def _log_meal(self, user_id: str, meal_type: str, foods: List[Dict], notes: str = "", mood: str = None) -> str:
        """Log a meal entry"""
        if user_id not in self.meal_history:
            self.meal_history[user_id] = []
        
        total_calories = sum(food.get('calories', 0) for food in foods)
        total_protein = sum(food.get('protein', 0) for food in foods)
        
        meal_entry = MealEntry(
            user_id=user_id,
            meal_type=meal_type,
            foods=foods,
            total_calories=total_calories,
            total_protein=total_protein,
            timestamp=datetime.now(),
            notes=notes,
            mood=mood
        )
        
        self.meal_history[user_id].append(meal_entry)
        return f"Logged {meal_type}: {total_calories} calories, {total_protein}g protein"
    
    def _get_meal_history(self, user_id: str, days: int = 7) -> str:
        """Get user's recent meal history"""
        if user_id not in self.meal_history:
            return "No meal history found."
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_meals = [
            meal for meal in self.meal_history[user_id]
            if meal.timestamp > cutoff_date
        ]
        
        if not recent_meals:
            return f"No meals logged in the last {days} days."
        
        total_calories = sum(meal.total_calories for meal in recent_meals)
        total_protein = sum(meal.total_protein for meal in recent_meals)
        
        summary = f"Last {days} days: {total_calories} total calories, {total_protein}g protein"
        return summary
    
    def _get_nutrition_advice(self, user_id: str, topic: str = "general") -> str:
        """Get personalized nutrition advice"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return "I'd love to give you personalized advice! Tell me about your goals first."
        
        # Get recent meal history for context
        recent_meals = self._get_meal_history(user_id, 3)
        
        advice_context = f"User: {profile.name}, Goals: {profile.goals}, Experience: {profile.experience_level}, Recent: {recent_meals}"
        return f"Based on your profile: {advice_context}"
    
    def get_memory(self, user_id: str):
        """Get or create conversation memory for user"""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationBufferWindowMemory(
                k=20,  # Keep recent context but not too much
                return_messages=True
            )
        return self.conversation_memories[user_id]
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process a user message with enhanced memory and context"""
        try:
            # Get user profile for context
            profile = self.user_profiles.get(user_id)
            
            # Get relevant memories from storage
            relevant_memories = self.memory_manager.get_relevant_memories(user_id, message, k=3)
            
            # Get conversation memory
            memory = self.get_memory(user_id)
            
            # Add user message to memory
            memory.chat_memory.add_user_message(message)
            
            # Get chat history
            chat_history = memory.chat_memory.messages
            
            # Create enhanced context
            context_parts = []
            
            if profile:
                context_parts.append(f"User: {profile.name}")
                if profile.goals:
                    context_parts.append(f"Goals: {', '.join(profile.goals)}")
                if profile.weight:
                    context_parts.append(f"Weight: {profile.weight}kg")
            
            if relevant_memories:
                context_parts.append("Recent context:")
                context_parts.extend(relevant_memories[:2])  # Top 2 most relevant
            
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
            
            # Store in persistent memory for future reference
            memory_type = self._classify_message_type(message)
            self.memory_manager.store_memory(
                user_id=user_id,
                message=message,
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
    def __init__(self, telegram_token: str, openai_api_key: str):
        self.telegram_token = telegram_token
        self.coach = NutritionCoachV2_1(openai_api_key, telegram_token)
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
            
            # Process with enhanced nutrition coach
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
        
        if not telegram_token or not openai_api_key:
            return {
                "statusCode": 500,
                "body": "Missing environment variables"
            }
        
        bot = TelegramNutritionBot(telegram_token, openai_api_key)
        
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