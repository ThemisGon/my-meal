from my_meal.agents.user_profile_agent import get_user_profile
from my_meal.agents.meal_planner_agent import generate_meal_or_plan
from my_meal.agents.meal_evaluation_agent import evaluate_meal_plan  # EvaluationResponse

MAX_ATTEMPTS = 3  # μέγιστες προσπάθειες για νέο πλάνο

def collect_user_input():
    goal = input("Ποιος είναι ο στόχος σου; (π.χ. απώλεια βάρους, ισορροπημένη διατροφή): ").strip()
    while not goal:
        goal = input("Υποχρεωτικό πεδίο. Ποιος είναι ο στόχος σου; ").strip()

    calories = input("Πόσες θερμίδες στοχεύεις την ημέρα; (π.χ. 2000): ").strip()
    while not calories.isdigit():
        calories = input("Δώσε έναν αριθμό. Πόσες θερμίδες στοχεύεις; ").strip()

    allergies = input("Έχεις αλλεργίες; (χώρισε με κόμμα, π.χ. ξηροί καρποί): ").strip()
    preferences = input("Διατροφικές προτιμήσεις; (π.χ. vegan, vegetarian): ").strip()
    time_of_day = input("Τι ώρα της ημέρας θέλεις το γεύμα; (π.χ. πρωινό, μεσημεριανό): ").strip()
    plan_scope = input("Εύρος πλάνου; (meal, day, month): ").strip()
    activity = input("Επίπεδο δραστηριότητας; (sedentary, active, etc.): ").strip()

    return f"""
    Στόχος: {goal}
    Θερμίδες: {calories}
    Αλλεργίες: {allergies}
    Προτιμήσεις: {preferences}
    Ώρα: {time_of_day}
    Πλάνο: {plan_scope}
    Δραστηριότητα: {activity}
    """

def main():
    user_input = collect_user_input()

    profile = get_user_profile(user_input)
    print("Προφίλ Χρήστη:\n", profile)

    attempt = 1
    while attempt <= MAX_ATTEMPTS:
        print(f"\nΠροσπάθεια #{attempt}")
        plan = generate_meal_or_plan(profile)
        print("Προτεινόμενο Πλάνο:\n", plan)

        evaluation = evaluate_meal_plan(profile, plan)

        print("Αξιολόγηση:")
        print("Status:", evaluation.status)
        print("Feedback:", evaluation.feedback)

        if evaluation.status == "OK":
            print("Το πλάνο εγκρίθηκε.")

            #Αποθήκευση πλάνου σε αρχείο
            with open("meal_plan_output.txt", "w", encoding="utf-8") as f:
                f.write(f"📌 Πλάνο για {profile.plan_scope.upper()}:\n\n")
                f.write(plan)

            #Αποθήκευση αξιολόγησης
            with open("evaluation.txt", "w", encoding="utf-8") as f:
                f.write(f"Status: {evaluation.status}\n")
                f.write(f"Feedback: {evaluation.feedback}\n")
                f.write(f"Suggestion: {evaluation.suggestion}\n")

            print("Meal plan και αξιολόγηση αποθηκεύτηκαν.")

            break

        elif evaluation.status == "REVIEW":
            print("Μικρά θέματα, αλλά αποδεκτό.")
            break
        else:
            print("Πρόβλημα με το πλάνο. Δημιουργείται νέο...")
            attempt += 1
    else:
        print("Δεν βρέθηκε κατάλληλο πλάνο μετά από 3 προσπάθειες.")

if __name__ == "__main__":
    main()
