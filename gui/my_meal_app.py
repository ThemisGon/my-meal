import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox
from datetime import datetime

from my_meal.agents.user_profile_agent import get_user_profile
from my_meal.agents.meal_planner_agent import generate_meal_or_plan
from my_meal.agents.meal_evaluation_agent import evaluate_meal_plan

# === Στρογγυλεμένο Πλαίσιο ===
def rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

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

# === Κεντρικό Παράθυρο ===
app = tb.Window(themename="flatly")
app.title("My Meal")
app.geometry("800x600")
app.configure(bg="#fcd9d9")

# === Canvas ===
canvas = tk.Canvas(app, bg="#fcd9d9", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# === Πλαίσιο Με Rounded Rectangle ===
x1, y1, x2, y2 = 150, 80, 650, 500
rounded_rectangle(canvas, x1, y1, x2, y2, radius=30, fill="#e25050", outline="")

# === Frame πάνω από το Canvas ===
form_frame = tk.Frame(canvas, bg="#e25050")
canvas.create_window((x1+40, y1+30), window=form_frame, anchor="nw")

# === Frame πάνω από το Canvas ===
form_bg = tk.Frame(canvas, bg="#e25050", width=x2-x1-80, height=y2-y1-60)
canvas.create_window((x1+40, y1+30), window=form_bg, anchor="nw")

form_frame = tk.Frame(form_bg, bg="#e25050")
form_frame.pack(fill="both", expand=True, padx=0, pady=0)


# === Τίτλος ===
tk.Label(form_frame, text="Create your meal", font=("Segoe UI", 18, "bold"), fg="white", bg="#e25050").grid(row=0, column=0, columnspan=3, pady=(0, 20))

row = 1

# === Επιλογές Plan Scope ===
plan_scope_var = tk.StringVar()
tk.Label(form_frame, text="Plan Scope:", fg="white", bg="#e25050", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, (label, value) in enumerate([("Next Meal", "next meal"), ("Day", "day"), ("Month", "month")]):
    tk.Radiobutton(form_frame, text=label, variable=plan_scope_var, value=value, bg="#e25050", fg="white", selectcolor="#e25050").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Goal ===
goal_var = tk.StringVar()
tk.Label(form_frame, text="Goal:", fg="white", bg="#e25050", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, val in enumerate(["Lose Weight", "Keep Weight", "Gain Weight"]):
    tk.Radiobutton(form_frame, text=val, variable=goal_var, value=val, bg="#e25050", fg="white", selectcolor="#e25050").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Activity Level ===
activity_var = tk.StringVar()
tk.Label(form_frame, text="Activity Level:", fg="white", bg="#e25050", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, val in enumerate(["Sedentary", "Active", "Very Active"]):
    tk.Radiobutton(form_frame, text=val, variable=activity_var, value=val, bg="#e25050", fg="white", selectcolor="#e25050").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

# === Εισαγωγικά Πεδία ===
entries = {}
for label in ["Calories Target", "Allergies", "Preferences"]:
    tk.Label(form_frame, text=label + ":", fg="white", bg="#e25050", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
    entry = tk.Entry(form_frame, width=35,  bg="#e25050", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="white")
    entry.grid(row=row, column=1, columnspan=2, sticky="w", pady=5)
    entries[label] = entry
    row += 1

# === Συνάρτηση Υποβολής ===
def submit():
    scope = plan_scope_var.get()
    goal = goal_var.get()
    activity = activity_var.get()
    calories = entries["Calories Target"].get().strip()
    allergies = entries["Allergies"].get().strip()
    preferences = entries["Preferences"].get().strip()

    if not scope or not goal or not calories.isdigit() or int(calories) < 100:
        messagebox.showerror("Error", "⚠️ Fill in all fields correctly.")
        return

    time_of_day = get_time_of_day() if scope == "next meal" else ""

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

        with open("meal_plan_output.txt", "w", encoding="utf-8") as f:
            f.write(plan)
        with open("evaluation.txt", "w", encoding="utf-8") as f:
            f.write(f"Status: {evaluation.status}\nFeedback: {evaluation.feedback}\nSuggestion: {evaluation.suggestion}")

        preview = "\n".join(plan.splitlines()[:12])
        messagebox.showinfo("✅ Plan Ready", preview)

    except Exception as e:
        messagebox.showerror("Σφάλμα", f"⚠️ Σφάλμα:\n{e}")

# === Button ===
tk.Button(form_frame, text="Create", width=30, command=submit, bg="#ffffff", fg="#e25050", activebackground="#f5f5f5", relief="flat", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, columnspan=3, pady=(20, 0))

app.mainloop()
