from langchain_core.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=EvaluationResponse)

class EvaluationResponse(BaseModel):
    status: str  # "OK", "REVIEW", or "WARNING"
    feedback: str
    suggestion: str

# Prompt για όλους τους τύπους πλάνου
template = ChatPromptTemplate.from_messages([
   ("system",
     """
        You are a nutrition evaluator. Check the meal plan against the user's goal, dietary restrictions, preferences, activity level, and plan scope (meal, day, month).

        Return structured output using ONLY the following format:\n{parser.get_format_instructions()}

        Respond strictly in this format:
        Status: OK/REVIEW/WARNING
        Feedback: [clear explanation why]
     """),
    ("human", "{input}")
])

# Σύνδεση με το LLM
chain = LLMChain(llm=llm, prompt=template)

#
def evaluate_meal_plan(profile: UserProfile, meal_plan: str) -> EvaluationResponse:
    prompt = (
        f"Evaluate the following meal plan for the following profile:\n"
        f"- Goal: {profile.goal}\n"
        f"- Calorie Target: {profile.calories_target}\n"
        f"- Allergies: {', '.join(profile.allergies)}\n"
        f"- Preferences: {', '.join(profile.preferences)}\n"
        f"- Activity Level: {profile.activity_level}\n"
        f"- Plan Scope: {profile.plan_scope}\n\n"
        f"-- MEAL PLAN --\n{meal_plan}"
    )
    result = chain.run({"input": prompt})
    return  parser.parse(result)  