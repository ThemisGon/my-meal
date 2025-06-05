from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from my_meal.agents.user_profile_agent import UserProfile
from my_meal.tools.calories_calculator import get_calories_for_item
from datetime import datetime

llm = OllamaLLM(model="llama3")

# Prompt για όλους τους τύπους πλάνου
template = ChatPromptTemplate.from_messages([
    ("system", 
        """You are a professional nutritionist that creates personalized meal plans or single meals.
        Use the user's goal, dietary restrictions, preferences, activity level and scope of the plan (meal, day, month) to generate the appropriate content.
        Respond clearly and structured."""
    ),
    ("human", "{input}")
])

parser = StrOutputParser()
# Σύνδεση με το LLM
chain = template | llm | parser

def get_time_of_day():
    hour = datetime.now().hour
    if hour < 11:
        return "breakfast"
    elif hour < 15:
        return "lunch"
    elif hour < 18:
        return "snack"
    else:
        return "dinner"

# Επιλογή είδους πλάνου με βάση το profile
def generate_meal_or_plan(profile: UserProfile) -> str:
    profile_info = (
        f"Goal: {profile.goal}\n"
        f"Calories Target: {profile.calories_target}\n"
        f"Allergies: {', '.join(profile.allergies)}\n"
        f"Preferences: {', '.join(profile.preferences)}\n"
        f"Activity level: {profile.activity_level}."
    )

     # Προειδοποίηση για πολύ χαμηλές θερμίδες
    calorie_warning = ""
    if int(profile.calories_target) < 200:
        calorie_warning = f"⚠️ WARNING: The calorie target is intentionally very low ({profile.calories_target}). Do not assume it's a typo.\n\n"

    if profile.plan_scope == "next meal":
        # Υπολογίζουμε αυτόματα την ώρα
        time_of_day = get_time_of_day()
        user_prompt = (
            calorie_warning +
            f"Create a {time_of_day} meal for someone with:\n"
            f"{profile_info}"
        )

    elif profile.plan_scope == "day":
        user_prompt = (
            calorie_warning +
            f"Create a one-day meal plan (breakfast, lunch, snack, dinner) for:\n"
            f"{profile_info}"
        )

    elif profile.plan_scope == "month":
        user_prompt = (
            calorie_warning +
            f"Create a 30-day monthly meal plan. Each day should have breakfast, lunch, snack, and dinner.\n"
            f"Ensure nutritional balance. Profile info:\n{profile_info}"
        )

    else:
        return "ERROR: Unrecognized plan scope."

    result = chain.invoke({"input": user_prompt})
    return str(result)