from agents.user_profile import get_user_profile
from agents.meal_planner_agent import generate_meal_or_plan
from agents.meal_evaluation_agent import evaluate_meal_plan  # EvaluationResponse

MAX_ATTEMPTS = 3  # μέγιστες προσπάθειες για νέο πλάνο

def main():
    user_input = """
    Θέλω διατροφή για μία ημέρα. Είμαι vegan, δεν τρώω ξηρούς καρπούς και στοχεύω σε 2000 θερμίδες.
    Δεν γυμνάζομαι. Θέλω μόνο το επόμενο γεύμα.
    """

    profile = get_user_profile(user_input)
    print("📌 Προφίλ Χρήστη:\n", profile)

    attempt = 1
    while attempt <= MAX_ATTEMPTS:
        print(f"\n🔁 Προσπάθεια #{attempt}")
        plan = generate_meal_or_plan(profile)
        print("🍽️ Προτεινόμενο Πλάνο:\n", plan)

        evaluation = evaluate_meal_plan(profile, plan)

        print("🧪 Αξιολόγηση:")
        print("Status:", evaluation.status)
        print("Feedback:", evaluation.feedback)

        if evaluation.status == "OK":
            print("✅ Το πλάνο εγκρίθηκε.")
            break
        elif evaluation.status == "REVIEW":
            print("⚠️ Μικρά θέματα, αλλά αποδεκτό.")
            break
        else:
            print("❌ Πρόβλημα με το πλάνο. Δημιουργείται νέο...")
            attempt += 1
    else:
        print("🚫 Δεν βρέθηκε κατάλληλο πλάνο μετά από 3 προσπάθειες.")
