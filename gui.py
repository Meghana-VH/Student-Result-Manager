# student_result_gui.py
"""
Student Result Manager - Tkinter GUI
Features:
- Add Student (roll, name, course)
- Add Marks (for subjects in the subjects table; initially adds default subjects if empty)
- View Result (total, percentage, grade)
- List Students (TreeView)
- Delete Student
- Uses SQLite DB: students.db
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from tkinter import simpledialog, messagebox
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")

print("DB FILE PATH:", os.path.abspath(DB))   # ← Helps you see where DB is saved

# ---------- Database helpers ----------
def get_conn():
    conn = sqlite3.connect(DB)
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        course TEXT
    )
    """)
    # subjects table (supports dynamic subjects later)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    # marks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        marks INTEGER NOT NULL,
        FOREIGN KEY (roll) REFERENCES students(roll),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )
    """)
    conn.commit()

    # if no subjects exist, insert default three subjects
    cur.execute("SELECT COUNT(*) FROM subjects")
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany("INSERT INTO subjects (name) VALUES (?)", [("Subject1",), ("Subject2",), ("Subject3",)])
        conn.commit()
    conn.close()

def add_student_to_db(roll, name, course):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO students (roll, name, course) VALUES (?, ?, ?)", (roll, name, course))
        conn.commit()
        return True, "Student added."
    except sqlite3.IntegrityError:
        return False, "A student with that roll number already exists."
    finally:
        conn.close()

def delete_student_from_db(roll):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM marks WHERE roll=?", (roll,))
    cur.execute("DELETE FROM students WHERE roll=?", (roll,))
    conn.commit()
    conn.close()

def list_students_db():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT roll, name, course FROM students ORDER BY roll")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_subjects():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, name FROM subjects ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_mark(roll, subject_id, marks):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO marks (roll, subject_id, marks) VALUES (?, ?, ?)", (roll, subject_id, marks))
    conn.commit()
    conn.close()

def get_marks_for_roll(roll):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT s.name, m.marks FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.roll = ?
        ORDER BY s.id
    """, (roll,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- Business logic ----------
def calculate_grade(percentage):
    if percentage >= 75:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 35:
        return "D"
    else:
        return "F"

# ---------- GUI ----------
class App:
    def __init__(self, master):
        self.master = master
        master.title("Student Result Manager")
        master.geometry("800x500")

        # Notebook (tabs)
        self.nb = ttk.Notebook(master)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_students = ttk.Frame(self.nb)
        self.tab_marks = ttk.Frame(self.nb)
        self.tab_results = ttk.Frame(self.nb)
        self.tab_admin = ttk.Frame(self.nb)

        self.nb.add(self.tab_students, text="Students")
        self.nb.add(self.tab_marks, text="Marks")
        self.nb.add(self.tab_results, text="Results")
        self.nb.add(self.tab_admin, text="Admin")

        self.build_students_tab()
        self.build_marks_tab()
        self.build_results_tab()
        self.build_admin_tab()

        self.refresh_students_list()

    # ---- Students tab ----
    def build_students_tab(self):
        frm_left = ttk.Frame(self.tab_students, padding=10)
        frm_left.pack(side="left", fill="y")

        ttk.Label(frm_left, text="Roll:").grid(row=0, column=0, sticky="w")
        self.ent_roll = ttk.Entry(frm_left)
        self.ent_roll.grid(row=0, column=1, pady=4)

        ttk.Label(frm_left, text="Name:").grid(row=1, column=0, sticky="w")
        self.ent_name = ttk.Entry(frm_left)
        self.ent_name.grid(row=1, column=1, pady=4)

        ttk.Label(frm_left, text="Course:").grid(row=2, column=0, sticky="w")
        self.ent_course = ttk.Entry(frm_left)
        self.ent_course.grid(row=2, column=1, pady=4)

        ttk.Button(frm_left, text="Add Student", command=self.add_student).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frm_left, text="Delete Student", command=self.delete_student).grid(row=4, column=0, columnspan=2, pady=6)
        ttk.Button(frm_left, text="Refresh List", command=self.refresh_students_list).grid(row=5, column=0, columnspan=2, pady=6)

        # Right: Treeview list of students
        frm_right = ttk.Frame(self.tab_students, padding=10)
        frm_right.pack(side="left", fill="both", expand=True)

        columns = ("roll", "name", "course")
        self.tree_students = ttk.Treeview(frm_right, columns=columns, show="headings")
        for col in columns:
            self.tree_students.heading(col, text=col.capitalize())
            self.tree_students.column(col, width=150)
        self.tree_students.pack(fill="both", expand=True)

    def add_student(self):
        roll = self.ent_roll.get().strip()
        name = self.ent_name.get().strip()
        course = self.ent_course.get().strip()
        if not roll or not name:
            messagebox.showwarning("Missing data", "Please enter both roll and name.")
            return
        ok, msg = add_student_to_db(roll, name, course)
        if ok:
            messagebox.showinfo("Success", msg)
            self.ent_roll.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.ent_course.delete(0, tk.END)
            self.refresh_students_list()
        else:
            messagebox.showerror("Error", msg)

    def delete_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a student in the list to delete.")
            return
        roll = self.tree_students.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete student {roll}?"):
            delete_student_from_db(roll)
            self.refresh_students_list()
            messagebox.showinfo("Deleted", f"Student {roll} deleted.")

    def refresh_students_list(self):
        for i in self.tree_students.get_children():
            self.tree_students.delete(i)
        for r, n, c in list_students_db():
            self.tree_students.insert("", tk.END, values=(r, n, c))

    # ---- Marks tab ----
    def build_marks_tab(self):
        frm = ttk.Frame(self.tab_marks, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.Frame(frm)
        left.pack(side="left", fill="y", padx=10)

        ttk.Label(left, text="Roll:").pack(anchor="w")
        self.ent_marks_roll = ttk.Entry(left); self.ent_marks_roll.pack(pady=4, fill="x")
        ttk.Button(left, text="Load Subjects", command=self.load_subjects_for_marks).pack(pady=6)

        self.subject_entries = []  # will hold (subject_id, label, entry)
        self.subjects_frame = ttk.Frame(left)
        self.subjects_frame.pack(fill="x", pady=6)

        ttk.Button(left, text="Save Marks", command=self.save_marks).pack(pady=10)

        # right: see existing marks for a roll
        right = ttk.Frame(frm)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="Existing Marks for Roll:").pack(anchor="w")
        self.list_marks = tk.Listbox(right)
        self.list_marks.pack(fill="both", expand=True)

    def load_subjects_for_marks(self):
        roll = self.ent_marks_roll.get().strip()
        if not roll:
            messagebox.showwarning("Missing", "Enter roll first.")
            return
        # clear previous entries
        for child in self.subjects_frame.winfo_children():
            child.destroy()
        self.subject_entries.clear()
        subjects = get_subjects()
        for sid, sname in subjects:
            lbl = ttk.Label(self.subjects_frame, text=sname)
            ent = ttk.Entry(self.subjects_frame)
            lbl.pack(anchor="w")
            ent.pack(fill="x", pady=2)
            self.subject_entries.append((sid, sname, ent))
        # show existing marks
        self.refresh_marks_list(roll)

    def save_marks(self):
        roll = self.ent_marks_roll.get().strip()
        if not roll:
            messagebox.showwarning("Missing", "Enter roll first.")
            return
        # ensure student exists
        students = {r for r,_,_ in list_students_db()}
        if roll not in students:
            messagebox.showerror("No such student", "Roll not found in students. Add student first.")
            return
        # save marks (delete existing marks for that roll first)
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM marks WHERE roll=?", (roll,))
        conn.commit()
        conn.close()
        any_saved = False
        for sid, sname, ent in self.subject_entries:
            val = ent.get().strip()
            if val == "":
                continue
            try:
                m = int(val)
                if m < 0 or m > 100:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Invalid", f"Marks for {sname} must be integer 0-100.")
                return
            add_mark(roll, sid, m)
            any_saved = True
        if any_saved:
            messagebox.showinfo("Saved", "Marks saved.")
            self.refresh_marks_list(roll)
        else:
            messagebox.showinfo("No data", "No marks entered.")

    def refresh_marks_list(self, roll):
        self.list_marks.delete(0, tk.END)
        rows = get_marks_for_roll(roll)
        if not rows:
            self.list_marks.insert(tk.END, "No marks found.")
            return
        for subj, m in rows:
            self.list_marks.insert(tk.END, f"{subj}: {m}")

    # ---- Results tab ----
    def build_results_tab(self):
        frm = ttk.Frame(self.tab_results, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(anchor="w")
        ttk.Label(top, text="Enter Roll:").pack(side="left")
        self.ent_res_roll = ttk.Entry(top); self.ent_res_roll.pack(side="left", padx=6)
        ttk.Button(top, text="Show Result", command=self.show_result).pack(side="left")

        self.txt_result = tk.Text(frm, height=15)
        self.txt_result.pack(fill="both", expand=True, pady=10)

        ttk.Button(frm, text="Export to PDF (placeholder)", command=self.export_pdf_placeholder).pack()

    def show_result(self):
        roll = self.ent_res_roll.get().strip()
        if not roll:
            messagebox.showwarning("Enter", "Enter roll.")
            return
        # get student
        students = {r:(n,c) for r,n,c in list_students_db()}
        if roll not in students:
            messagebox.showerror("Not found", "Roll not found.")
            return
        name, course = students[roll]
        marks = get_marks_for_roll(roll)
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, f"Roll: {roll}\nName: {name}\nCourse: {course}\n\n")
        if not marks:
            self.txt_result.insert(tk.END, "No marks found.\n")
            return
        total = 0
        count = 0
        for subj, m in marks:
            self.txt_result.insert(tk.END, f"{subj}: {m}\n")
            total += m
            count += 1
        percentage = total / count if count else 0
        grade = calculate_grade(percentage)
        status = "Pass" if percentage >= 35 else "Fail"
        self.txt_result.insert(tk.END, f"\nTotal: {total}\nPercentage: {percentage:.2f}%\nGrade: {grade}\nStatus: {status}\n")

    def export_pdf_placeholder(self):
        messagebox.showinfo("Export", "PDF export will be implemented in the next step (ReportLab).")

    # ---- Admin tab: subject management (simple) ----
    def build_admin_tab(self):
        frm = ttk.Frame(self.tab_admin, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.Frame(frm)
        left.pack(side="left", fill="y", padx=10)
        ttk.Label(left, text="Add Subject:").pack(anchor="w")
        self.ent_new_subject = ttk.Entry(left)
        self.ent_new_subject.pack(fill="x", pady=4)
        ttk.Button(left, text="Add", command=self.add_subject).pack(pady=6)

        ttk.Label(left, text="Remove Subject (select from list):").pack(anchor="w", pady=(10,0))
        ttk.Button(left, text="Remove Selected", command=self.remove_selected_subject).pack(pady=6)

        right = ttk.Frame(frm)
        right.pack(side="left", fill="both", expand=True)
        self.tree_subjects = ttk.Treeview(right, columns=("id","name"), show="headings")
        self.tree_subjects.heading("id", text="ID")
        self.tree_subjects.heading("name", text="Name")
        self.tree_subjects.pack(fill="both", expand=True)
        self.refresh_subjects()

    def add_subject(self):
        name = self.ent_new_subject.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Enter subject name.")
            return
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
            messagebox.showinfo("Added", f"Subject '{name}' added.")
            self.ent_new_subject.delete(0, tk.END)
            self.refresh_subjects()
        except sqlite3.IntegrityError:
            messagebox.showerror("Exists", "Subject already exists.")
        finally:
            conn.close()

    def remove_selected_subject(self):
        sel = self.tree_subjects.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a subject to remove.")
            return
        sid = self.tree_subjects.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Removing a subject will delete related marks. Continue?"):
            conn = get_conn(); cur = conn.cursor()
            cur.execute("DELETE FROM marks WHERE subject_id=?", (sid,))
            cur.execute("DELETE FROM subjects WHERE id=?", (sid,))
            conn.commit(); conn.close()
            messagebox.showinfo("Removed", "Subject removed.")
            self.refresh_subjects()

    def refresh_subjects(self):
        for i in self.tree_subjects.get_children():
            self.tree_subjects.delete(i)
        for sid, name in get_subjects():
            self.tree_subjects.insert("", tk.END, values=(sid, name))
        # refresh marks tab input fields if open
        # (optional) we won't auto reload; user should click "Load Subjects"
def open_login_window():
     login = tk.Tk()
     login.title("Login")
     login.geometry("350x250")

     tk.Label(login, text="Login System", font=("Arial", 18, "bold")).pack(pady=10)

     tk.Label(login, text="Username").pack()
     username_entry = tk.Entry(login)
     username_entry.pack()

     tk.Label(login, text="Password").pack()
     password_entry = tk.Entry(login, show="*")
     password_entry.pack()

     def check_login():
         user = username_entry.get()
         pwd = password_entry.get()

         if user == "" or pwd == "":
            messagebox.showerror("Error", "All fields are required")
            return

        # ---- Default admin login ----
         if user == "admin" and pwd == "admin123":
            messagebox.showinfo("Success", "Login Successful")
            login.destroy()

            # Open your existing GUI
            root = tk.Tk()
            app = App(root)
            root.mainloop()

         else:
            messagebox.showerror("Invalid", "Wrong Username or Password")

     tk.Button(login, text="Login", width=15, command=check_login).pack(pady=10)

     login.mainloop()

# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    open_login_window()


