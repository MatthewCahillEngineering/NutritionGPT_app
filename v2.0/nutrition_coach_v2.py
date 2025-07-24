"""
NutritionGPT Coach v2.0 - Conversational AI Nutrition Assistant
Built with LangChain, memory, and advanced AI features
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Pydantic for data validation
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
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
    created_at: datetime = None
    
    def __post_init__(self):
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.goals is None:
            self.goals = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class MealEntry:
    user_id: str
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[Dict[str, Any]]  # [{"name": "chicken", "calories": 200, "protein": 25}]
    total_calories: int
    total_protein: float
    timestamp: datetime
    notes: Optional[str] = None

@dataclass
class NutritionPlan:
    user_id: str
    plan_type: str  # daily, weekly, custom
    meals: List[Dict[str, Any]]
    total_calories: int
    total_protein: float
    created_at: datetime
    notes: Optional[str] = None

class NutritionCoach:
    def __init__(self, openai_api_key: str, telegram_token: str):
        self.openai_api_key = openai_api_key
        self.telegram_token = telegram_token
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # Initialize memory systems
        self.conversation_memories = {}  # user_id -> memory
        self.user_profiles = {}  # user_id -> UserProfile
        self.meal_history = {}  # user_id -> List[MealEntry]
        self.nutrition_plans = {}  # user_id -> List[NutritionPlan]
        
        # Initialize vector store for RAG
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vector_store = None
        self._initialize_vector_store()
        
        # Initialize tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _initialize_vector_store(self):
        """Initialize vector store with nutrition knowledge base"""
        nutrition_knowledge = [
            "High protein foods include chicken breast, fish, eggs, Greek yogurt, and legumes.",
            "Complex carbohydrates like whole grains, sweet potatoes, and quinoa provide sustained energy.",
            "Healthy fats from avocados, nuts, olive oil, and fatty fish support brain health.",
            "Fiber-rich foods like vegetables, fruits, and whole grains support digestive health.",
            "Hydration is crucial - aim for 8-10 glasses of water daily.",
            "Meal timing can affect energy levels - eat every 3-4 hours.",
            "Protein should be 20-30% of daily calories for muscle building.",
            "Carbohydrates should be 45-65% of daily calories for energy.",
            "Fats should be 20-35% of daily calories for hormone production.",
            "Micronutrients from colorful vegetables and fruits support overall health."
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.create_documents(nutrition_knowledge)
        
        self.vector_store = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            collection_name="nutrition_knowledge"
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the AI agent"""
        tools = [
            Tool(
                name="get_user_profile",
                func=self._get_user_profile,
                description="Get user's nutrition profile and preferences"
            ),
            Tool(
                name="update_user_profile",
                func=self._update_user_profile,
                description="Update user's nutrition profile and preferences"
            ),
            Tool(
                name="log_meal",
                func=self._log_meal,
                description="Log a meal with foods, calories, and protein"
            ),
            Tool(
                name="get_meal_history",
                func=self._get_meal_history,
                description="Get user's recent meal history"
            ),
            Tool(
                name="create_nutrition_plan",
                func=self._create_nutrition_plan,
                description="Create a personalized nutrition plan"
            ),
            Tool(
                name="calculate_calories",
                func=self._calculate_calories,
                description="Calculate calories and macros for foods"
            ),
            Tool(
                name="get_nutrition_advice",
                func=self._get_nutrition_advice,
                description="Get personalized nutrition advice based on user data"
            ),
            Tool(
                name="schedule_reminder",
                func=self._schedule_reminder,
                description="Schedule a reminder for meals or hydration"
            )
        ]
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the AI agent with conversation memory"""
        system_prompt = """You are NutritionGPT, a friendly and knowledgeable AI nutrition coach. 
        
        Your role is to:
        1. Help users track their nutrition and eating habits
        2. Create personalized meal plans and nutrition advice
        3. Remember user preferences and goals
        4. Provide encouraging and supportive guidance
        5. Ask follow-up questions to better understand user needs
        
        Always be conversational, supportive, and educational. Use the available tools to:
        - Access and update user profiles
        - Log meals and track nutrition
        - Create personalized plans
        - Provide evidence-based advice
        
        Be proactive in asking about user goals, preferences, and current eating habits."""
        
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
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        return f"Updated profile for user {user_id}: {asdict(profile)}"
    
    def _log_meal(self, user_id: str, meal_type: str, foods: List[Dict], notes: str = "") -> str:
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
            notes=notes
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
        
        summary = f"Recent meals (last {days} days):\n"
        for meal in recent_meals:
            summary += f"- {meal.meal_type}: {meal.total_calories} cal, {meal.total_protein}g protein\n"
        
        return summary
    
    def _create_nutrition_plan(self, user_id: str, plan_type: str = "daily") -> str:
        """Create a personalized nutrition plan"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return "Please set up your profile first with goals and preferences."
        
        # Create plan using AI
        plan_prompt = f"""
        Create a {plan_type} nutrition plan for a user with:
        - Goals: {profile.goals}
        - Dietary restrictions: {profile.dietary_restrictions}
        - Calorie target: {profile.calorie_target}
        - Protein target: {profile.protein_target}
        
        Provide specific meals with foods, portions, and nutrition info.
        """
        
        response = self.llm.invoke(plan_prompt)
        
        # Store the plan
        plan = NutritionPlan(
            user_id=user_id,
            plan_type=plan_type,
            meals=[],  # Would parse from AI response
            total_calories=profile.calorie_target or 2000,
            total_protein=profile.protein_target or 150,
            created_at=datetime.now(),
            notes=response.content
        )
        
        if user_id not in self.nutrition_plans:
            self.nutrition_plans[user_id] = []
        self.nutrition_plans[user_id].append(plan)
        
        return f"Created {plan_type} nutrition plan:\n{response.content}"
    
    def _calculate_calories(self, foods: List[str]) -> str:
        """Calculate calories and macros for foods"""
        # This would integrate with a nutrition database API
        # For now, return estimated values
        return f"Estimated nutrition for {foods}: Calories vary by portion size. Use a food tracking app for precise values."
    
    def _get_nutrition_advice(self, user_id: str, topic: str = "general") -> str:
        """Get personalized nutrition advice"""
        profile = self.user_profiles.get(user_id)
        meal_history = self.meal_history.get(user_id, [])
        
        context = f"""
        User Profile: {asdict(profile) if profile else 'No profile'}
        Recent Meals: {len(meal_history)} meals logged
        Topic: {topic}
        """
        
        # Query vector store for relevant knowledge
        docs = self.vector_store.similarity_search(topic, k=3)
        knowledge = "\n".join([doc.page_content for doc in docs])
        
        advice_prompt = f"""
        Based on this context and nutrition knowledge, provide personalized advice:
        
        Context: {context}
        Knowledge: {knowledge}
        
        Provide specific, actionable advice for this user.
        """
        
        response = self.llm.invoke(advice_prompt)
        return response.content
    
    def _schedule_reminder(self, user_id: str, reminder_type: str, time: str) -> str:
        """Schedule a reminder (would integrate with scheduling system)"""
        return f"Scheduled {reminder_type} reminder for {time} for user {user_id}"
    
    def get_memory(self, user_id: str):
        """Get or create conversation memory for user"""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationBufferWindowMemory(
                k=50,  # Increased from 10 to 50 messages for better memory
                return_messages=True
            )
        return self.conversation_memories[user_id]
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process a user message and return response"""
        try:
            # Get user's conversation memory
            memory = self.get_memory(user_id)
            
            # Add user message to memory
            memory.chat_memory.add_user_message(message)
            
            # Get chat history
            chat_history = memory.chat_memory.messages
            
            # Run agent with memory
            response = self.agent.invoke({
                "input": message,
                "chat_history": chat_history
            })
            
            # Add AI response to memory
            memory.chat_memory.add_ai_message(response["output"])
            
            return response["output"]
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm having trouble processing that right now. Could you try rephrasing?"
    
    def send_proactive_message(self, user_id: str, message_type: str) -> str:
        """Send proactive messages based on time, goals, etc."""
        profile = self.user_profiles.get(user_id)
        
        if message_type == "meal_reminder":
            return "Hey! Don't forget to log your meal. What did you eat?"
        elif message_type == "hydration_reminder":
            return "Time to hydrate! Have you had enough water today?"
        elif message_type == "goal_check":
            if profile and profile.goals:
                return f"How are you progressing toward your goals: {', '.join(profile.goals)}?"
            else:
                return "How are your nutrition goals going today?"
        
        return "How's your nutrition journey going?"

# Telegram Bot Integration
class TelegramNutritionBot:
    def __init__(self, telegram_token: str, openai_api_key: str):
        self.telegram_token = telegram_token
        self.coach = NutritionCoach(openai_api_key, telegram_token)
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
            
            # Process with nutrition coach
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
        
        # Process Telegram update
        result = bot.handle_message(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    # Test the nutrition coach
    coach = NutritionCoach(
        openai_api_key="your-openai-key",
        telegram_token="your-telegram-token"
    )
    
    # Test conversation
    response = coach.process_message("test_user", "Hi! I want to start tracking my nutrition and build muscle.")
    print(response) 