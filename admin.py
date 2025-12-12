from tkinter import *
from tkinter import ttk, messagebox
import sqlite3

# DB Connection
def get_connection():
    return sqlite3.connect("students.db")

# --------------------------
# ADMIN DASHBOARD WINDOW
# --------------------------
def admin_dashboard():

    admin_win = Toplevel()
    admin_win.title("Admin Dashboard")
    admin_win.geometry("700x500")
    admin_win.config(bg="white")

    title = Label(admin_win, text="Admin Dashboard",
                  font=("Arial", 20, "bold"), bg="white")
    title.pack(pady=10)

    # --------------------------
    # TREEVIEW TABLE
    # --------------------------
    columns = ("id", "name", "s1", "s2", "s3", "total", "percentage", "grade")
    table = ttk.Treeview(admin_win, columns=columns, show='headings')

    for col in columns:
        table.heading(col, text=col.upper())

    table.pack(fill=BOTH, expand=True, pady=10)

    # --------------------------
    # FETCH STUDENTS
    # --------------------------
    def load_data():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        rows = cur.fetchall()
        table.delete(*table.get_children())
        for r in rows:
            table.insert("", END, values=r)
        conn.close()

    load_data()

    # --------------------------
    # ADD STUDENT
    # --------------------------
    def add_student():
        def save_student():
            name = name_entry.get()
            s1 = s1_entry.get()
            s2 = s2_entry.get()
            s3 = s3_entry.get()

            if name == "" or s1 == "" or s2 == "" or s3 == "":
                messagebox.showerror("Error", "All fields required")
                return

            s1, s2, s3 = int(s1), int(s2), int(s3)
            total = s1 + s2 + s3
            percentage = total / 3

            if percentage >= 75:
                grade = "A"
            elif percentage >= 60:
                grade = "B"
            elif percentage >= 50:
                grade = "C"
            elif percentage >= 35:
                grade = "D"
            else:
                grade = "F"

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO students(name, s1, s2, s3, total, percentage, grade) VALUES(?,?,?,?,?,?,?)",
                        (name, s1, s2, s3, total, percentage, grade))
            conn.commit()
            conn.close()
            load_data()
            add_win.destroy()
            messagebox.showinfo("Success", "Student added successfully")

        add_win = Toplevel(admin_win)
        add_win.title("Add Student")
        add_win.geometry("300x300")

        Label(add_win, text="Name").pack()
        name_entry = Entry(add_win)
        name_entry.pack()

        Label(add_win, text="Subject 1").pack()
        s1_entry = Entry(add_win)
        s1_entry.pack()

        Label(add_win, text="Subject 2").pack()
        s2_entry = Entry(add_win)
        s2_entry.pack()

        Label(add_win, text="Subject 3").pack()
        s3_entry = Entry(add_win)
        s3_entry.pack()

        Button(add_win, text="Save", command=save_student).pack(pady=10)

    # --------------------------
    # UPDATE STUDENT
    # --------------------------
    def update_student():
        selected = table.focus()
        if selected == "":
            messagebox.showwarning("Select", "Select a student from table")
            return

        values = table.item(selected, "values")
        sid, name_old, old1, old2, old3, total_old, pct_old, grade_old = values

        def save_update():
            s1 = int(s1_entry.get())
            s2 = int(s2_entry.get())
            s3 = int(s3_entry.get())

            total = s1 + s2 + s3
            percentage = total / 3

            if percentage >= 75:
                grade = "A"
            elif percentage >= 60:
                grade = "B"
            elif percentage >= 50:
                grade = "C"
            elif percentage >= 35:
                grade = "D"
            else:
                grade = "F"

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE students SET s1=?, s2=?, s3=?, total=?, percentage=?, grade=? WHERE id=?
            """, (s1, s2, s3, total, percentage, grade, sid))
            conn.commit()
            conn.close()

            load_data()
            upd_win.destroy()
            messagebox.showinfo("Updated", "Student marks updated")

        upd_win = Toplevel(admin_win)
        upd_win.title("Update Marks")
        upd_win.geometry("300x250")

        Label(upd_win, text="Subject 1").pack()
        s1_entry = Entry(upd_win)
        s1_entry.insert(0, old1)
        s1_entry.pack()

        Label(upd_win, text="Subject 2").pack()
        s2_entry = Entry(upd_win)
        s2_entry.insert(0, old2)
        s2_entry.pack()

        Label(upd_win, text="Subject 3").pack()
        s3_entry = Entry(upd_win)
        s3_entry.insert(0, old3)
        s3_entry.pack()

        Button(upd_win, text="Update", command=save_update).pack(pady=10)

    # --------------------------
    # DELETE STUDENT
    # --------------------------
    def delete_student():
        selected = table.focus()
        if selected == "":
            messagebox.showwarning("Select", "Select a student")
            return

        sid = table.item(selected, "values")[0]

        confirm = messagebox.askyesno("Confirm", "Delete this student?")
        if confirm:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            load_data()
            messagebox.showinfo("Deleted", "Student deleted")
    from reportlab.pdfgen import canvas

    def export_pdf():
        selected = table.focus()
        if selected == "":
            messagebox.showwarning("Select", "Select a student to export PDF")
            return

        values = table.item(selected, "values")
        sid, name, s1, s2, s3, total, percentage, grade = values

        file_name = f"{name}_result.pdf"
        c = canvas.Canvas(file_name)

        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, 800, "Student Result")

        c.setFont("Helvetica", 12)
        c.drawString(50, 760, f"ID: {sid}")
        c.drawString(50, 740, f"Name: {name}")
        c.drawString(50, 720, f"Subject 1: {s1}")
        c.drawString(50, 700, f"Subject 2: {s2}")
        c.drawString(50, 680, f"Subject 3: {s3}")
        c.drawString(50, 660, f"Total: {total}")
        c.drawString(50, 640, f"Percentage: {percentage}")
        c.drawString(50, 620, f"Grade: {grade}")

        c.save()

        messagebox.showinfo("Success", f"PDF saved as {file_name}")

    # --------------------------
    # BUTTONS
    # --------------------------
    frame = Frame(admin_win, bg="white")
    frame.pack(pady=10)

    Button(frame, text="Add Student", command=add_student, width=15).grid(row=0, column=0, padx=10)
    Button(frame, text="Update Marks", command=update_student, width=15).grid(row=0, column=1, padx=10)
    Button(frame, text="Delete Student", command=delete_student, width=15).grid(row=0, column=2, padx=10)
    Button(frame, text="Refresh", command=load_data, width=15).grid(row=0, column=3, padx=10)
    Button(frame, text="Logout", command=admin_win.destroy, width=15).grid(row=0, column=4, padx=10)
    Button(frame, text="Export PDF", command=export_pdf, width=15).grid(row=0, column=5, padx=10)

if __name__ == "__main__":
    root = Tk()
    root.withdraw()   # hide empty main window
    admin_dashboard() # open admin window
    root.mainloop()
