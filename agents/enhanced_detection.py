from my_meal.tools.ingredient_extractor_tool import _extract_ingredients_logic

def detect_allergens_in_meal(meal_text: str, allergens: list[str]) -> list[str]:
    detected = set()
    lines = meal_text.splitlines()

    for line in lines:
        if not line.strip() or ":" not in line:
            continue
        try:
            ingredients = _extract_ingredients_logic(line)
            for allergen in allergens:
                for ingredient in ingredients:
                    if allergen.lower() in ingredient.lower():
                        detected.add(allergen.lower())
        except Exception as e:
            print(f"[ERROR] Αποτυχία ανάλυσης γραμμής: '{line}' → {e}")
            continue

    return list(detected)