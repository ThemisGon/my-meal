from langchain_core.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.chains import LLMChain

class UserProfile(BaseModel):
    goal: str
    calories_target: int
    allergies: list[str]
    preferences: list[str]
    time_of_day: str
    plan_scope: str
    activity_level: str

llm = Ollama(model="llama3")

template = ChatPromptTemplate.from_messages([
    ("system", "You are a nutrition assistant that extracts user goals and preferences."),
    ("human", "{input}")
])

chain = LLMChain(llm=llm, prompt=template)

def get_user_profile(user_input: str):
    return chain.run({"input": user_input})