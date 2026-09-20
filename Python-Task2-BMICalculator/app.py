import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvasTkAgg = None
    Figure = None


DB_FILE = Path(__file__).with_name("bmi_records.db")


class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator - OIBSIP")
        self.root.geometry("900x650")
        self.root.minsize(780, 580)

        self.current_user = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Enter your details and click Calculate")
        self.category_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        self.record_saved_for_current_input = False

        self.setup_database()
        self.build_ui()

    def setup_database(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        recorded_at TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not initialize the database.\n\n{error}"
            )

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="BMI Calculator",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="OASIS INFOBYTE • Python Programming • Task 2",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        main = ttk.Frame(self.root, padding=(20, 5, 20, 20))
        main.pack(fill="both", expand=True)

        input_card = ttk.LabelFrame(main, text="User Details", padding=18)
        input_card.pack(fill="x")

        ttk.Label(input_card, text="User Name:").grid(row=0, column=0, sticky="w", padx=5, pady=7)
        ttk.Entry(input_card, textvariable=self.current_user, width=30).grid(
            row=0, column=1, sticky="ew", padx=5, pady=7
        )

        ttk.Label(input_card, text="Weight (kg):").grid(row=1, column=0, sticky="w", padx=5, pady=7)
        ttk.Entry(input_card, textvariable=self.weight_var, width=30).grid(
            row=1, column=1, sticky="ew", padx=5, pady=7
        )

        ttk.Label(input_card, text="Height (m):").grid(row=2, column=0, sticky="w", padx=5, pady=7)
        ttk.Entry(input_card, textvariable=self.height_var, width=30).grid(
            row=2, column=1, sticky="ew", padx=5, pady=7
        )

        input_card.columnconfigure(1, weight=1)

        button_row = ttk.Frame(input_card)
        button_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

        ttk.Button(button_row, text="Calculate BMI", command=self.calculate_bmi).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(button_row, text="View History", command=self.show_history).pack(
            side="left", padx=8
        )
        ttk.Button(button_row, text="Show Trend", command=self.show_trend).pack(
            side="left", padx=8
        )
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(
            side="left", padx=8
        )

        result_card = ttk.LabelFrame(main, text="BMI Result", padding=18)
        result_card.pack(fill="x", pady=15)

        self.result_label = tk.Label(
            result_card,
            textvariable=self.result_var,
            font=("Segoe UI", 20, "bold"),
            anchor="center"
        )
        self.result_label.pack(fill="x", pady=(5, 8))

        self.category_label = tk.Label(
            result_card,
            textvariable=self.category_var,
            font=("Segoe UI", 14, "bold"),
            anchor="center"
        )
        self.category_label.pack(fill="x")

        info = ttk.Label(
            main,
            text=(
                "Categories: Underweight < 18.5  •  Normal 18.5–24.9  •  "
                "Overweight 25–29.9  •  Obese ≥ 30"
            ),
            font=("Segoe UI", 9)
        )
        info.pack(pady=(2, 5))

        ttk.Label(
            main,
            textvariable=self.status_var,
            anchor="w"
        ).pack(fill="x", side="bottom", pady=(8, 0))

    def classify_bmi(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    def calculate_bmi(self):
        if self.record_saved_for_current_input:
            messagebox.showinfo(
                "Record Already Saved",
                "This BMI record is already saved. Click Clear before entering a new record."
            )
            return

        name = self.current_user.get().strip()
        weight_text = self.weight_var.get().strip()
        height_text = self.height_var.get().strip()

        if not name:
            messagebox.showerror("Invalid Input", "Please enter a user name.")
            return

        try:
            weight = float(weight_text)
            height = float(height_text)
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Weight and height must be numeric values."
            )
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Weight and height must be greater than zero."
            )
            return

        bmi = weight / (height ** 2)
        category = self.classify_bmi(bmi)

        self.result_var.set(f"BMI: {bmi:.2f}")
        self.category_var.set(category)
        self.set_result_style(category)

        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    """
                    INSERT INTO bmi_records
                    (user_name, weight, height, bmi, category, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        weight,
                        height,
                        bmi,
                        category,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()
            self.record_saved_for_current_input = True
            self.status_var.set(f"Record saved for {name}.")
        except sqlite3.Error as error:
            self.status_var.set("Database save failed.")
            messagebox.showerror(
                "Database Error",
                f"BMI was calculated, but the record could not be saved.\n\n{error}"
            )

    def set_result_style(self, category):
        # Tkinter uses the default system colors; this gives clear visual feedback.
        category_styles = {
            "Underweight": ("#1565C0", "#E3F2FD"),
            "Normal": ("#2E7D32", "#E8F5E9"),
            "Overweight": ("#EF6C00", "#FFF3E0"),
            "Obese": ("#C62828", "#FFEBEE"),
        }
        foreground, background = category_styles.get(category, ("black", "white"))
        self.result_label.configure(fg=foreground, bg=background)
        self.category_label.configure(fg=foreground, bg=background)
        self.result_label.master.configure(style="Result.TLabelframe")

    def clear_form(self):
        self.current_user.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.result_var.set("Enter your details and click Calculate")
        self.category_var.set("")
        self.result_label.configure(fg="black", bg=self.root.cget("bg"))
        self.category_label.configure(fg="black", bg=self.root.cget("bg"))
        self.record_saved_for_current_input = False
        self.status_var.set("Form cleared. Enter the next user details.")

    def fetch_history(self, user_name=None):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                return conn.execute(
                    """
                    SELECT user_name, recorded_at, weight, height, bmi, category
                    FROM bmi_records
                    ORDER BY id ASC
                    """
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
            return []

    def fetch_user_history(self, user_name):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                return conn.execute(
                    """
                    SELECT recorded_at, weight, height, bmi, category
                    FROM bmi_records
                    WHERE user_name = ?
                    ORDER BY id ASC
                    """,
                    (user_name,),
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
            return []

    def show_history(self):
        rows = self.fetch_history()
        if not rows:
            messagebox.showinfo("History", "No BMI records have been saved yet.")
            return

        window = tk.Toplevel(self.root)
        window.title("BMI History - All Users")
        window.geometry("850x450")

        columns = ("user", "date", "weight", "height", "bmi", "category")
        tree = ttk.Treeview(window, columns=columns, show="headings")
        headings = {
            "user": "User",
            "date": "Date",
            "weight": "Weight (kg)",
            "height": "Height (m)",
            "bmi": "BMI",
            "category": "Category",
        }
        widths = {
            "user": 120, "date": 150, "weight": 110,
            "height": 110, "bmi": 100, "category": 130
        }

        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=widths[column], anchor="center")

        for row in rows:
            user, date, weight, height, bmi, category = row
            tree.insert(
                "",
                "end",
                values=(user, date, f"{weight:.1f}", f"{height:.2f}", f"{bmi:.2f}", category),
            )

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

    def show_trend(self):
        if Figure is None or FigureCanvasTkAgg is None:
            messagebox.showerror(
                "Missing Package",
                "Matplotlib is not installed.\nRun: pip install matplotlib"
            )
            return

        name = self.current_user.get().strip()
        if not name:
            messagebox.showerror("Missing User", "Enter a user name first.")
            return

        rows = self.fetch_user_history(name)
        if len(rows) < 1:
            messagebox.showinfo("Trend", f"No BMI records found for {name}.")
            return

        dates = [row[0] for row in rows]
        bmi_values = [row[3] for row in rows]

        window = tk.Toplevel(self.root)
        window.title(f"BMI Trend - {name}")
        window.geometry("800x520")

        figure = Figure(figsize=(8, 4.8), dpi=100)
        axis = figure.add_subplot(111)
        axis.plot(range(1, len(bmi_values) + 1), bmi_values, marker="o")
        axis.set_title(f"BMI Trend for {name}")
        axis.set_xlabel("Record Number")
        axis.set_ylabel("BMI")
        axis.grid(True, alpha=0.3)

        for index, (bmi, date) in enumerate(zip(bmi_values, dates), start=1):
            axis.annotate(
                date,
                (index, bmi),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=7,
            )

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


def main():
    root = tk.Tk()
    BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
