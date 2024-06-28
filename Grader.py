import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import threading
import hashlib
import sqlite3
from datetime import datetime

class GraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grader")
        self.root.geometry("800x900")
        self.root.resizable(False, False)
        self.setup_styles()
        self.setup_ui()
        self.create_database()

        self.df_key = None  # To store the key data

    def setup_styles(self):
        self.style = ttk.Style("superhero")

    def setup_ui(self):
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Enter PIN:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.pin_entry = ttk.Entry(self.login_frame, show="*", font=("Helvetica", 14), width=20, bootstyle="success")
        self.pin_entry.grid(row=0, column=1, padx=10, pady=10)
        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.check_pin, bootstyle="primary-outline")
        self.login_button.grid(row=0, column=2, padx=10, pady=10)

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(expand=True)
        self.main_frame.pack_forget()

        ttk.Label(self.main_frame, text="Trainee Name:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.trainee_name_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), width=30, bootstyle="info")
        self.trainee_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.main_frame, text="Date:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10)
        self.date_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), width=30, bootstyle="info")
        self.date_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.main_frame, text="Exercise:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=10)
        self.exercise_entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), width=30, bootstyle="info")
        self.exercise_entry.grid(row=2, column=1, padx=10, pady=10)

        button_frame = ttk.Frame(self.main_frame, padding="20")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Upload Key Data", command=self.upload_key_data, bootstyle="success-outline").grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(button_frame, text="Upload Trainee Data", command=self.upload_trainee_data, bootstyle="success-outline").grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(button_frame, text="View Previous Results", command=self.view_previous_results, bootstyle="info-outline").grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(button_frame, text="Export Trainee's Result", command=self.export_trainee_result, bootstyle="warning-outline").grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(button_frame, text="Export All", command=self.export_all_results, bootstyle="danger-outline").grid(row=4, column=0, padx=10, pady=5)

        self.tree = ttk.Treeview(self.main_frame, columns=("Column", "Accuracy"), show='headings', bootstyle="primary")
        self.tree.heading("Column", text="Column")
        self.tree.heading("Accuracy", text="Accuracy")
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def check_pin(self):
        pin = self.pin_entry.get()
        if self.verify_pin(pin):
            self.login_frame.pack_forget()
            self.main_frame.pack(expand=True)
        else:
            messagebox.showerror("Error", "Incorrect PIN")

    def verify_pin(self, pin):
        default_pin_hash = hashlib.sha256("1414".encode()).hexdigest()
        entered_pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return entered_pin_hash == default_pin_hash

    def upload_key_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            threading.Thread(target=self.process_key_data, args=(file_path,)).start()

    def process_key_data(self, file_path):
        try:
            self.df_key = pd.read_excel(file_path)
            messagebox.showinfo("Success", "Key data uploaded and analyzed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upload_trainee_data(self):
        if self.df_key is None:
            messagebox.showerror("Error", "Please upload key data first.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            threading.Thread(target=self.process_trainee_data, args=(file_path,)).start()

    def process_trainee_data(self, file_path):
        try:
            df_trainee = pd.read_excel(file_path)
            comparison_result = self.compare_data(df_trainee)

            self.tree.delete(*self.tree.get_children())
            for column, accuracy in comparison_result.items():
                self.tree.insert("", tk.END, values=(column, f"{accuracy:.2f}%"))
            
            trainee_name = self.trainee_name_entry.get()
            date = self.date_entry.get()
            exercise = self.exercise_entry.get()
            self.save_result(trainee_name, date, exercise, comparison_result)
            self.generate_report(trainee_name, date, exercise, comparison_result)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def compare_data(self, df_trainee):
        comparison_result = {}
        for column in self.df_key.columns:
            if column in df_trainee.columns:
                key_values = self.df_key[column].fillna("").astype(str)
                trainee_values = df_trainee[column].fillna("").astype(str)
                match_count = (key_values == trainee_values).sum()
                total_count = len(key_values)
                accuracy = (match_count / total_count) * 100
                comparison_result[column] = accuracy
            else:
                comparison_result[column] = 0.0  # No matching column found
        return comparison_result

    def generate_report(self, trainee_name, date, exercise, comparison_result):
        report_path = f"{trainee_name}_{date}_{exercise}_comparison_report.xlsx"
        report_df = pd.DataFrame(list(comparison_result.items()), columns=["Column", "Accuracy"])
        report_df.to_excel(report_path, index=False)
        messagebox.showinfo("Report Generated", f"Report saved as {report_path}")

    def create_database(self):
        self.conn = sqlite3.connect('comparison_results.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                trainee_name TEXT,
                date TEXT,
                exercise TEXT,
                column TEXT,
                accuracy REAL
            )
        ''')
        self.conn.commit()

    def save_result(self, trainee_name, date, exercise, comparison_result):
        for column, accuracy in comparison_result.items():
            self.cursor.execute('''
                INSERT INTO results (trainee_name, date, exercise, column, accuracy)
                VALUES (?, ?, ?, ?, ?)
            ''', (trainee_name, date, exercise, column, accuracy))
        self.conn.commit()

    def view_previous_results(self):
        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Previous Results")
        self.results_window.geometry("800x500")

        self.results_tree = ttk.Treeview(self.results_window, columns=("Trainee", "Date", "Exercise", "Column", "Accuracy"), show='headings', bootstyle="info")
        self.results_tree.heading("Trainee", text="Trainee")
        self.results_tree.heading("Date", text="Date")
        self.results_tree.heading("Exercise", text="Exercise")
        self.results_tree.heading("Column", text="Column")
        self.results_tree.heading("Accuracy", text="Accuracy")
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.results_window.columnconfigure(0, weight=1)
        self.results_window.rowconfigure(0, weight=1)

        self.cursor.execute('SELECT trainee_name, date, exercise, column, accuracy FROM results')
        for row in self.cursor.fetchall():
            self.results_tree.insert("", tk.END, values=row)

    def export_trainee_result(self):
        trainee_name = self.trainee_name_entry.get()
        date = self.date_entry.get()
        exercise = self.exercise_entry.get()
        if not trainee_name or not date or not exercise:
            messagebox.showerror("Error", "Please enter Trainee Name, Date, and Exercise to export results.")
            return

        report_path = f"{trainee_name}_{date}_{exercise}_export.xlsx"
        self.cursor.execute('SELECT trainee_name, date, exercise, column, accuracy FROM results WHERE trainee_name=? AND date=? AND exercise=?', 
                            (trainee_name, date, exercise))
        result_data = self.cursor.fetchall()
        
        if result_data:
            report_df = pd.DataFrame(result_data, columns=["Trainee", "Date", "Exercise", "Column", "Accuracy"])
            report_df.to_excel(report_path, index=False)
            messagebox.showinfo("Export Successful", f"Trainee's result exported to {report_path}")
        else:
            messagebox.showerror("Error", "No results found for the specified Trainee, Date, and Exercise.")

    def export_all_results(self):
        report_path = "all_results_export.xlsx"
        self.cursor.execute('SELECT trainee_name, date, exercise, column, accuracy FROM results')
        result_data = self.cursor.fetchall()

        if result_data:
            report_df = pd.DataFrame(result_data, columns=["Trainee", "Date", "Exercise", "Column", "Accuracy"])
            report_df.to_excel(report_path, index=False)
            messagebox.showinfo("Export Successful", f"All results exported to {report_path}")
        else:
            messagebox.showerror("Error", "No results found to export.")

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = GraderApp(root)
    root.mainloop()
