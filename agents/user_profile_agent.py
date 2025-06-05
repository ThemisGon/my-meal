from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
import json
from langchain_core.output_parsers import StrOutputParser
from typing import List

llm = OllamaLLM(model="llama3")

class UserProfile(BaseModel):
    goal: str
    calories_target: int
    allergies: List[str] = []
    preferences: List[str] = []
    time_of_day: str
    plan_scope: str
    activity_level: str

template = ChatPromptTemplate.from_messages([
    ("system", "You are a nutrition assistant that extracts user goals and preferences from the user's input and returns ONLY a JSON object with the following format:\n"
           '{{ "goal": str, "calories_target": int, "allergies": [str], "preferences": [str], "time_of_day": str, "plan_scope": str, "activity_level": str }}'
),
    ("human", "{input}")
])
parser = StrOutputParser()
chain = template | llm | parser

def get_user_profile(user_input: str) -> UserProfile:
    response = chain.invoke({"input": user_input})
    raw_text = response
    print("🧠 RAW LLM OUTPUT:\n", raw_text)

    import re, json

    # Βρες το JSON block
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        print("⚠️ Δεν βρέθηκε JSON:\n", raw_text)
        raise ValueError("Το LLM δεν επέστρεψε σωστό JSON")

    json_str = match.group()
    profile_dict = json.loads(json_str)

    # ✅ Βάλε εδώ το μπλοκ ελέγχου:
    required_fields = ["goal", "calories_target", "allergies", "preferences", "time_of_day", "plan_scope", "activity_level"]
    for field in required_fields:
        if field not in profile_dict:
            profile_dict[field] = [] if field in ["allergies", "preferences"] else ""

    # Μετά κάνε parse με το καθαρισμένο dict
    return UserProfile(**profile_dict)
