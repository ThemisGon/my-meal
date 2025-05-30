import requests
import os
from dotenv import load_dotenv

load_dotenv()

NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

def get_calories_for_item(item_name: str) -> float:
    if not NUTRITIONIX_APP_ID or not NUTRITIONIX_API_KEY:
        raise EnvironmentError("Missing Nutritionix credentials in environment variables.")

    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "query": item_name,
        "timezone": "Europe/Athens"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise ValueError(f"Nutritionix error: {response.status_code} - {response.text}")

    nutrients = response.json()
    calories = 0.0
    for food in nutrients.get("foods", []):
        calories += food.get("nf_calories", 0.0)

    return calories
