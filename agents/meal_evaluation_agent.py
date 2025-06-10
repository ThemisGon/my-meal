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
    status: str 
    feedback: str
    suggestion: str


parser = PydanticOutputParser(pydantic_object=EvaluationResponse)

format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

template = ChatPromptTemplate.from_messages([
    ("system",
     f"""
        Repeat: DO NOT include any allergens.

        You are a strict nutrition evaluator. Your job is to evaluate the meal plan against the user's goal, allergies, preferences, activity level, and plan scope (meal, day, month).

        NEVER include any items that appear in the user's allergies list — even indirectly or in derivatives. For example:
        - If the allergy is "nuts", almond butter, peanuts, and granola with nuts are all forbidden.
        - If the allergy is "chicken", grilled chicken, chicken salad, and turkey are also forbidden.
        - If the allergy is "legumes", lentils and chickpeas are included.

        The same logic applies to **any other allergy** the user specifies. Always avoid **direct and indirect forms**, **derivatives**, and **cooked variations** of all allergens.

        In long outputs (like monthly plans), make sure to repeat the user's allergies and preferences at the start of each week to prevent mistakes.

        Return a valid JSON object in the following format:
        {format_instructions}

        Do NOT include any extra explanation, markdown or text before or after the JSON.

        Return structured output using ONLY the above format.
        Always include a meaningful, non-empty "suggestion" field — even if it's just a healthy habit tip.
    """),
    ("human", "{input}")
])

llm = OllamaLLM(model="llama3")

chain = template | llm | parser

def detect_allergens_in_meal(meal_text, allergens):
    detected = []
    lower_meal = meal_text.lower()
    for allergen in allergens:
        if re.search(rf"\b{re.escape(allergen.lower())}\b", lower_meal):
            detected.append(allergen)
    return detected

def estimate_total_calories(meal_plan_text: str) -> float:
    food_lines = re.findall(r'[*+-]\s+([^\n]+)', meal_plan_text)
    total = 0.0

    for line in food_lines:
        try:
            calories = get_calories_for_item(line)
            print(f"🧮 {line} ≈ {calories:.0f} kcal")
            total += calories
        except Exception as e:
            print(f"Πρόβλημα με '{line}': {e}")
            continue

    return total


def evaluate_meal_plan(profile: UserProfile, meal_plan: str) -> EvaluationResponse:
    estimated_calories = estimate_total_calories(meal_plan)

    prompt = (
        f"Evaluate the following meal plan for the following profile:\n"
        f"- Goal: {profile.goal}\n"
        f"- Calorie Target: {profile.calories_target}\n"
        f"- Estimated Calories: {estimated_calories:.0f}\n"
        f"- ⚠️ Allergies (STRICT AVOIDANCE): {', '.join(profile.allergies)}\n"
        f"- Preferences: {', '.join(profile.preferences)}\n"
        f"- Activity Level: {profile.activity_level}\n"
        f"- Plan Scope: {profile.plan_scope}\n\n"
        f"-- MEAL PLAN --\n{meal_plan}"
    )

    found = detect_allergens_in_meal(meal_plan, profile.allergies)
    if found:
        return EvaluationResponse(
            status="WARNING",
            feedback=f"The meal plan contains allergenic items: {', '.join(found)}.",
            suggestion="Please regenerate a meal plan without these allergens."
        )

    result = chain.invoke({"input": prompt})  
    if not isinstance(result, EvaluationResponse):
        raise TypeError(f"⚠️ Το evaluation δεν είναι EvaluationResponse. Πήραμε: {type(result)}")
    return result