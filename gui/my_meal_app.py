import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from my_meal.agents.user_profile_agent import get_user_profile
from my_meal.agents.meal_planner_agent import generate_meal_or_plan
from my_meal.agents.meal_evaluation_agent import evaluate_meal_plan


# Στρογγυλεμένο Πλαίσιο
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

#Κεντρικό Παράθυρο
app = tk.Tk()
app.title("My Meal")
app.geometry("800x600")
app.configure(bg="#F5CECE")

#Canvas 
canvas = tk.Canvas(app, bg="#fff0f0", highlightthickness=0)
canvas.pack(fill="both", expand=True)

#Πλαίσιο Με Rounded Rectangle
x1, y1, x2, y2 = 125, 80, 675, 500
rounded_rectangle(canvas, x1, y1, x2, y2, radius=30, fill="#eb5e5e", outline="")

#Container πάνω από το Canvas
container = tk.Frame(canvas, width=510, height=370, bg="#eb5e5e")
container.pack_propagate(False)
canvas.create_window((x1+40, y1+30), window=container, anchor="nw")

#Form μέσα στο Container
form_frame = tk.Frame(container, bg="#eb5e5e")
form_frame.pack(fill="both", expand=True)

form_frame.columnconfigure(0, weight=1)
form_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(2, weight=1)

#Τίτλος
tk.Label(
    form_frame,
    text="Create your meal",
    font=("Segoe UI", 18, "bold"),
    fg="white", bg="#eb5e5e"
).grid(row=0, column=1, columnspan=2, padx=(0, 10), pady=(0, 20), sticky="ew")

form_frame.columnconfigure(0, weight=1)
form_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(2, weight=1)

row = 1

#Επιλογές Plan Scope
plan_scope_var = tk.StringVar()
tk.Label(form_frame, text="Plan Scope:", fg="white", bg="#eb5e5e",
         font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, (label, value) in enumerate([("Next Meal", "next meal"), ("Day", "day"), ("Month", "month")]):
    tk.Radiobutton(form_frame, text=label, variable=plan_scope_var, value=value,
                   bg="#eb5e5e", fg="white", selectcolor="#eb5e5e").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

#Goal
goal_var = tk.StringVar()
tk.Label(form_frame, text="Goal:", fg="white", bg="#eb5e5e",
         font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, val in enumerate(["Lose Weight", "Keep Weight", "Gain Weight"]):
    tk.Radiobutton(form_frame, text=val, variable=goal_var, value=val,
                   bg="#eb5e5e", fg="white", selectcolor="#eb5e5e").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

#Activity Level
activity_var = tk.StringVar()
tk.Label(form_frame, text="Activity Level:", fg="white", bg="#eb5e5e",
         font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")
for i, val in enumerate(["Sedentary", "Active", "Very Active"]):
    tk.Radiobutton(form_frame, text=val, variable=activity_var, value=val,
                   bg="#eb5e5e", fg="white", selectcolor="#eb5e5e").grid(row=row, column=i+1, padx=5, sticky="w")
row += 1

#Εισαγωγικά Πεδία
entries = {}
for label in ["Calories Target", "Allergies", "Preferences"]:
    tk.Label(form_frame, text=label + ":", fg="white", bg="#eb5e5e",
             font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
    entry = tk.Text(form_frame, width=35, height=1, bg="white", fg="black",
                    insertbackground="black", relief="flat", highlightthickness=0, borderwidth=0, padx=5, pady=4)
    entry.grid(row=row, column=1, columnspan=2, sticky="w", pady=5, padx=(10, 0))
    entry.configure(highlightthickness=0, bd=0, insertbackground="black", padx=5)
    entries[label] = entry
    row += 1

def only_valid_chars(text):
    return all(
        char.isalpha() or char.isspace() or char in [","]
        for char in text.strip()
    )

def submit():
    scope = plan_scope_var.get()
    goal = goal_var.get()
    activity = activity_var.get()
    calories = entries["Calories Target"].get("1.0", "end-1c").strip()
    allergies = entries["Allergies"].get("1.0", "end-1c").strip()
    preferences = entries["Preferences"].get("1.0", "end-1c").strip()
    if not scope or not goal or not activity or not calories.isdigit() or not only_valid_chars(allergies) or not only_valid_chars(preferences):
        messagebox.showerror("Error", "Fill in all fields correctly.")
        return
    if int(calories) < 100 or int(calories) > 3500:
        messagebox.showerror("Error", "Fill in all fields correctly.")
        return
    if any(item in preferences.lower() for item in allergies.lower().split(",")):
        messagebox.showerror("Conflict", "Το ίδιο στοιχείο υπάρχει και σε αλλεργία και σε προτίμηση.")
        return

    time_of_day = get_time_of_day() if scope == "next meal" else ""

    def split_text_list(txt):
        return [x.strip().lower() for x in re.split(r"[,\s]+", txt) if x.strip()]

    allergies_list = split_text_list(allergies)
    preferences_list = split_text_list(preferences)

    prompt = f"""
    Στόχος: {goal}
    Θερμίδες: {calories}
    Αλλεργίες: {', '.join(allergies_list)}
    Προτιμήσεις: {', '.join(preferences_list)}
    Ώρα: {time_of_day}
    Πλάνο: {scope}
    Δραστηριότητα: {activity}
    """


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
            f.write(
                f"Status: {evaluation.status}\nFeedback: {evaluation.feedback}\nSuggestion: {evaluation.suggestion}"
            )

        preview = "\n".join(plan.splitlines()[:12])
        messagebox.showinfo("Plan Ready", preview)

    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα:\n{e}")

tk.Button(
    form_frame,
    text="Create",
    width=30,
    command=submit,
    bg="#2c3e50",
    fg="white",
    activebackground="#34495e",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    padx=10,
    pady=6
).grid(row=row, column=1, columnspan=2, pady=(20, 0), sticky="ew")

app.mainloop()
