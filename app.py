from database import setup_database, get_connection


def calculate_result(s1, s2, s3):
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
    status = "PASS" if percentage >= 35 else "FAIL"
    return total, percentage, grade, status


def input_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be >= {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be <= {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def add_student():
    print("\n--- ADD STUDENT ---")
    roll = input_int("Enter Roll Number: ", min_value=1)
    name = input("Enter Student Name: ").strip()
    course = input("Enter Course: ").strip()

    if not name or not course:
        print("Name and Course cannot be empty.\n")
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        # Check if roll already exists
        cursor.execute("SELECT 1 FROM students WHERE roll = ?", (roll,))
        if cursor.fetchone():
            print("Roll number already exists.\n")
            return

        cursor.execute(
            "INSERT INTO students (roll, name, course) VALUES (?, ?, ?)",
            (roll, name, course),
        )
        conn.commit()
    print("Student Added Successfully!\n")


def add_or_update_marks():
    print("\n--- ADD / UPDATE MARKS ---")
    roll = input_int("Enter Roll Number: ", min_value=1)

    s1 = input_int("Enter Subject 1 Marks (0-100): ", 0, 100)
    s2 = input_int("Enter Subject 2 Marks (0-100): ", 0, 100)
    s3 = input_int("Enter Subject 3 Marks (0-100): ", 0, 100)

    total, percentage, grade, status = calculate_result(s1, s2, s3)

    with get_connection() as conn:
        cursor = conn.cursor()

        # Ensure student exists
        cursor.execute("SELECT 1 FROM students WHERE roll = ?", (roll,))
        if not cursor.fetchone():
            print("Student not found. Add the student first.\n")
            return

        cursor.execute("""
            INSERT INTO results (roll, subject1, subject2, subject3, total, percentage, grade, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(roll) DO UPDATE SET
                subject1=excluded.subject1,
                subject2=excluded.subject2,
                subject3=excluded.subject3,
                total=excluded.total,
                percentage=excluded.percentage,
                grade=excluded.grade,
                status=excluded.status
        """, (roll, s1, s2, s3, total, percentage, grade, status))

        conn.commit()

    print("Marks Saved Successfully!\n")


def view_result():
    print("\n--- VIEW RESULT ---")
    roll = input_int("Enter Roll Number to View Result: ", min_value=1)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.roll, s.name, s.course,
                   r.subject1, r.subject2, r.subject3,
                   r.total, r.percentage, r.grade, r.status
            FROM students s
            LEFT JOIN results r ON s.roll = r.roll
            WHERE s.roll = ?
        """, (roll,))
        row = cursor.fetchone()

    if row:
        print("\n--- STUDENT RESULT ---")
        print("Roll Number :", row[0])
        print("Name        :", row[1])
        print("Course      :", row[2])

        if row[3] is None:
            print("Marks       : Not entered yet.\n")
        else:
            print("Marks       :", row[3], row[4], row[5])
            print("Total       :", row[6])
            print("Percentage  :", round(row[7], 2), "%")
            print("Grade       :", row[8])
            print("Status      :", row[9], "\n")
    else:
        print("Record Not Found!\n")


def list_all_students():
    print("\n--- ALL STUDENTS ---")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT roll, name, course FROM students ORDER BY roll")
        rows = cursor.fetchall()

    if not rows:
        print("No students found.\n")
        return

    for r in rows:
        print(f"Roll: {r[0]} | Name: {r[1]} | Course: {r[2]}")
    print()


def list_results_summary():
    print("\n--- RESULTS SUMMARY (TOP TO LOW) ---")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.roll, s.name, s.course,
                   r.total, r.percentage, r.grade, r.status
            FROM students s
            JOIN results r ON s.roll = r.roll
            ORDER BY r.percentage DESC
        """)
        rows = cursor.fetchall()

    if not rows:
        print("No results found.\n")
        return

    for r in rows:
        print(
            f"Roll: {r[0]} | Name: {r[1]} | Course: {r[2]} | "
            f"Total: {r[3]} | %: {round(r[4], 2)} | Grade: {r[5]} | Status: {r[6]}"
        )
    print()


def delete_student():
    print("\n--- DELETE STUDENT ---")
    roll = input_int("Enter Roll Number to Delete: ", min_value=1)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM students WHERE roll = ?", (roll,))
        if not cursor.fetchone():
            print("Student not found.\n")
            return

        cursor.execute("DELETE FROM students WHERE roll = ?", (roll,))
        conn.commit()

    print("Student and related results deleted.\n")


def menu():
    setup_database()

    while True:
        print("=== STUDENT RESULT MANAGER ===")
        print("1. Add Student")
        print("2. Add / Update Marks")
        print("3. View Result by Roll")
        print("4. List All Students")
        print("5. List Results Summary")
        print("6. Delete Student")
        print("7. Exit")

        choice = input_int("Enter Your Choice: ", 1, 7)

        if choice == 1:
            add_student()
        elif choice == 2:
            add_or_update_marks()
        elif choice == 3:
            view_result()
        elif choice == 4:
            list_all_students()
        elif choice == 5:
            list_results_summary()
        elif choice == 6:
            delete_student()
        elif choice == 7:
            print("Exiting...")
            break


if __name__ == "__main__":
    menu()
