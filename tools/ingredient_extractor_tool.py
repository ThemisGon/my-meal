import re
from langchain_core.tools import tool


def _extract_ingredients_logic(meal_description: str) -> list:
    """
    Extracts ingredients from the provided input data for meal analysis.
    """
    raw_ingredients = re.split(
        r"[,\-\(\)]|\bwith\b|\bκαι\b|\bσε\b|\bon\b|\bof\b|\bserved\b|\band\b",
        meal_description,
        flags=re.IGNORECASE
    )
    banned_keywords = ["-free", "free-", "without", "no ", "dairy-free", "χωρίς"]

    ingredients = [
        ingredient.strip().lower()
        for ingredient in raw_ingredients
        if ingredient.strip() and not any(bad in ingredient.lower() for bad in banned_keywords)
    ]

    return ingredients


from langchain_core.tools import tool

@tool
def extract_ingredients(meal_description: str) -> list:
    """Extracts ingredients from a meal description for use in LangChain tools."""
    return _extract_ingredients_logic(meal_description)
