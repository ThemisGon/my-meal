from langchain_core.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.chains import LLMChain

# Prompt για όλους τους τύπους πλάνου
template = ChatPromptTemplate.from_messages([
    ("system", 
        """You are a professional nutritionist that creates personalized meal plans or single meals.
        Use the user's goal, dietary restrictions, preferences, activity level and scope of the plan (meal, day, month) to generate the appropriate content.
        Respond clearly and structured."""
    ),
    ("human", "{input}")
])

# Σύνδεση με το LLM
chain = LLMChain(llm=llm, prompt=template)

# Επιλογή είδους πλάνου με βάση το profile
def generate_meal_or_plan(profile: UserProfile) -> str:
    profile_info = (
        f"-A goal of: {profile.goal}\n"
        f"-A calorie target of: {profile.calories_target}\n"
        f"-Allergies at: {', '.join(profile.allergies)}, "
        f"-Preferences at: {', '.join(profile.preferences)}, "
        f"-Activity level: {profile.activity_level}."
    )
    if profile.plan_scope == "meal":
        user_prompt = (
            f"For this time of day {profile.time_of_day},Create the perfect meal for a person with:\n"
            f"{profile_info}"
        )
    elseif profile.plan_scope == "day":
        user_prompt = (
            f"Create a meal plan for a day for a person with:\n"
            f"{profile_info}"
        )
    elseif profile.plan_scope == "month":
        user_prompt = (
            f"Create a meal plan for a month for a person with:\n"
            f"{profile_info}"
        )
    else:
        user_prompt = "ERROR: Unrecognized plan scope."
    
    result = chain.run({"input": user_prompt})
    return result