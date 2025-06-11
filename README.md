# My-Meal – Intelligent Meal Planning Assistant

**My Meal** is an intelligent agent-based system that generates and evaluates personalized meal plans based on user goals, allergies, preferences, and activity levels. It uses LLMs (via LangChain & Ollama) to simulate a professional dietitian workflow.

---

## Features

- Personalized meal plan generation (next meal, daily, monthly)
- Allergy & preference-aware meal evaluation
- Automatic calorie estimation (via Nutritionix API)
- User profile extraction from natural language
- Two modes:
  - **Command Line Interface (CLI)**
  - **Graphical User Interface (GUI) with Tkinter**

---

## Architecture (Multi-Agent System)
The system is composed of multiple collaborative agents and tools working in a structured agentic workflow:
### Agents

| Agent Name             | Role                                                                 |
|------------------------|----------------------------------------------------------------------|
| `UserProfileAgent`     | Extracts structured user information (goals, allergies, preferences, etc.) from free-form text   |
| `MealPlannerAgent`     | Generates a meal plan based on user profile and selected plan scope (meal/day/month)             |
| `MealEvaluationAgent`  | Evaluates the generated meal plan against user constraints and offers feedback/suggestions   |
| `EnhancedDetectionAgent` | Scans the plan for allergenic ingredients using text parsing and cross-checking        |

### Tools

| Tool Name              | Function                                                              |
|------------------------|----------------------------------------------------------------------|
| `CaloriesCalculator`   | Uses Nutritionix API to estimate caloric content for each food item                          |
| `IngredientExtractorTool` | Extracts potential ingredients from meal plan text using regular expressions               |

## Flow Overview
![Image](https://github.com/user-attachments/assets/c3455a5a-86cb-4029-941d-90ac5408292f)
