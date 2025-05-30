import tkinter as tk

from tkinter import messagebox
from datetime import datetime
from my_meal.agents.user_profile_agent import get_user_profile
from my_meal.agents.meal_planner_agent import generate_meal_or_plan
from my_meal.agents.meal_evaluation_agent import evaluate_meal_plan

# === Utilities ===
def get_time_of_day():
    hour = datetime.now().hour
    if hour < 11:
        return "breakfast"
    elif hour < 15:
        return "lunch"
    elif hour < 18:
        return "snack"
    else:
        return "dinner"

# === Styling ===
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_ENTRY = ("Segoe UI", 10)
BG_COLOR = "#f5f5f5"
LABEL_COLOR = "#333"

# === Main Window ===
root = tk.Tk()
root.title("My Meal")
root.geometry("800x600")
root.configure(bg=BG_COLOR)

frame = tk.Frame(root, bg=BG_COLOR)
frame.place(relx=0.5, rely=0.5, anchor="center")

row = 0

# === Welcome Label ===
tk.Label(frame, text="👋 Welcome to My-Meal", font=("Segoe UI", 16, "bold"), bg=BG_COLOR).grid(row=row, column=0, columnspan=4, pady=10)
row += 1

# === Plan Scope Selection ===
plan_scope_var = tk.StringVar()

tk.Label(frame, text="📅 Εύρος Πλάνου:", font=FONT_LABEL, bg=BG_COLOR, fg=LABEL_COLOR).grid(row=row, column=0, sticky="e", pady=5)
for i, (label, value) in enumerate([("Next Meal", "next meal"), ("Day", "day"), ("Month", "month")]):
    tk.Radiobutton(frame, text=label, variable=plan_scope_var, value=value, font=FONT_ENTRY, bg=BG_COLOR).grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Goal Selection ===
goal_var = tk.StringVar()
tk.Label(frame, text="🎯 Στόχος:", font=FONT_LABEL, bg=BG_COLOR).grid(row=row, column=0, sticky="e", pady=5)
for i, val in enumerate(["Lose Weight", "Keep Weight", "Gain Weight"]):
    tk.Radiobutton(frame, text=val, variable=goal_var, value=val, font=FONT_ENTRY, bg=BG_COLOR).grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Activity Level ===
activity_var = tk.StringVar()
tk.Label(frame, text="🏃 Δραστηριότητα:", font=FONT_LABEL, bg=BG_COLOR).grid(row=row, column=0, sticky="e", pady=5)
for i, val in enumerate(["Sedentary", "Active", "Very Active"]):
    tk.Radiobutton(frame, text=val, variable=activity_var, value=val, font=FONT_ENTRY, bg=BG_COLOR).grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Fields with entries ===
entries = {}
for label_text in ["Θερμίδες", "Αλλεργίες", "Προτιμήσεις"]:
    tk.Label(frame, text=label_text + ":", font=FONT_LABEL, bg=BG_COLOR, fg=LABEL_COLOR).grid(row=row, column=0, sticky="e", pady=5)
    entry = tk.Entry(frame, font=FONT_ENTRY, width=40)
    entry.grid(row=row, column=1, columnspan=3, padx=5, sticky="w")
    entries[label_text] = entry
    row += 1

# === Submit Button ===
def submit():
    scope = plan_scope_var.get()
    if not scope:
        messagebox.showerror("Σφάλμα", "❗ Διάλεξε εύρος πλάνου.")
        return

    goal = goal_var.get()
    calories = entries["Θερμίδες"].get().strip()
    allergies = entries["Αλλεργίες"].get().strip()
    preferences = entries["Προτιμήσεις"].get().strip()
    activity = activity_var.get()

    if not goal or not calories.isdigit():
        messagebox.showerror("Σφάλμα", "❗ Συμπλήρωσε σωστά τον στόχο και τις θερμίδες.")
        return

    if int(calories) < 100:
        messagebox.showerror("Σφάλμα", "❗ Οι θερμίδες πρέπει να είναι πάνω από 100.")
        return

    time_of_day = get_time_of_day() if scope == "next meal" else ""

    # Σύνθεση prompt για agent
    prompt = f"""
    Στόχος: {goal}
    Θερμίδες: {calories}
    Αλλεργίες: {allergies}
    Προτιμήσεις: {preferences}
    Ώρα: {time_of_day}

    Πλάνο: {scope}
    Δραστηριότητα: {activity}
    """

    try:
        profile = get_user_profile(prompt)
        plan = generate_meal_or_plan(profile)
        evaluation = evaluate_meal_plan(profile, plan)

        result = f"📌 Πλάνο ({scope}):\n\n{plan}\n\n🧪 Αξιολόγηση:\nStatus: {evaluation.status}\nFeedback: {evaluation.feedback}"

        preview = "\n".join(plan.splitlines()[:15])  # δείχνει τις πρώτες 15 γραμμές
        messagebox.showinfo("✅ Πλάνο Δημιουργήθηκε", preview)

        with open("meal_plan_output.txt", "w", encoding="utf-8") as f:
            f.write(plan)

        with open("evaluation.txt", "w", encoding="utf-8") as f:
            f.write(f"Status: {evaluation.status}\nFeedback: {evaluation.feedback}\nSuggestion: {evaluation.suggestion}")

    except Exception as e:
        messagebox.showerror("Σφάλμα", f"⚠️ Σφάλμα κατά την παραγωγή πλάνου:\n{e}")

tk.Button(frame, text="📝 Δημιουργία Πλάνου", font=FONT_LABEL, bg="#4a90e2", fg="white", width=30, command=submit).grid(row=row, column=0, columnspan=4, pady=20)

root.mainloop()
