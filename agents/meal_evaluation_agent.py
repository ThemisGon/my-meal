import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel
from my_meal.agents.user_profile_agent import UserProfile
from my_meal.tools.calories_calculator import get_calories_for_item


class EvaluationResponse(BaseModel):
    status: str  # "OK", "REVIEW", or "WARNING"
    feedback: str
    suggestion: str


parser = PydanticOutputParser(pydantic_object=EvaluationResponse)

format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

template = ChatPromptTemplate.from_messages([
    ("system",
     f"""
        You are a nutrition evaluator. Check the meal plan against the user's goal, dietary restrictions, preferences, activity level, and plan scope (meal, day, month).

        Return structured output using ONLY the following format:
        {format_instructions}
        Always include a non-empty "suggestion" field, even if it's just a healthy eating tip or reinforcement of good habits.
     """),
    ("human", "{input}")
])

llm = OllamaLLM(model="llama3")

chain = template | llm | parser


def estimate_total_calories(meal_plan_text: str) -> float:
    food_lines = re.findall(r'[*+-]\s+([^\n]+)', meal_plan_text)
    total = 0.0

    for line in food_lines:
        try:
            calories = get_calories_for_item(line)
            print(f"🧮 {line} ≈ {calories:.0f} kcal")
            total += calories
        except Exception as e:
            print(f"⚠️ Πρόβλημα με '{line}': {e}")
            continue

    return total


def evaluate_meal_plan(profile: UserProfile, meal_plan: str) -> EvaluationResponse:
    estimated_calories = estimate_total_calories(meal_plan)

    prompt = (
        f"Evaluate the following meal plan for the following profile:\n"
        f"- Goal: {profile.goal}\n"
        f"- Calorie Target: {profile.calories_target}\n"
        f"- Estimated Calories: {estimated_calories:.0f}\n"
        f"- Allergies: {', '.join(profile.allergies)}\n"
        f"- Preferences: {', '.join(profile.preferences)}\n"
        f"- Activity Level: {profile.activity_level}\n"
        f"- Plan Scope: {profile.plan_scope}\n\n"
        f"-- MEAL PLAN --\n{meal_plan}"
    )

    result = chain.invoke({"input": prompt})  # result είναι ήδη EvaluationResponse
    if not isinstance(result, EvaluationResponse):
        raise TypeError(f"⚠️ Το evaluation δεν είναι EvaluationResponse. Πήραμε: {type(result)}")
    return result