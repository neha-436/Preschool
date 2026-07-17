from flask import Flask, request, render_template, url_for, flash, redirect, session, Blueprint
from db import db, cursor
from datetime import date

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"] != "teacher":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    
    # Get teacher's assigned class
    cursor.execute("""
        SELECT class_assigned
        FROM teachers
        WHERE user_id=%s
    """, (session["user_id"],))

    teacher = cursor.fetchone()

    selected_class = teacher["class_assigned"]

    selected_date = request.args.get(
        "attendance_date",
        date.today().isoformat()
    )

    # Get students of that class
    cursor.execute("""
        SELECT *
        FROM students
        WHERE class_name=%s
        ORDER BY name
    """, (selected_class,))

    students = cursor.fetchall()

    cursor.execute("""
        SELECT student_id, status
        FROM attendance
        WHERE attendance_date=%s
        AND class_name=%s
    """, (selected_date, selected_class))

    records = cursor.fetchall()

    attendance_map = {}

    for record in records:
        attendance_map[record["student_id"]] = record["status"]

    if request.method == "POST":
        attendance_date = request.form["attendance_date"]

        for student in students:
            status = request.form.get(f"status_{student['id']}")

            cursor.execute("""
                INSERT INTO attendance
                (student_id, attendance_date, status, class_name, marked_by)
                VALUES (%s, %s, %s, %s, %s) 
                           
                ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                class_name = VALUES(class_name),
                marked_by = VALUES(marked_by)
                           
            """, (
                student["id"],
                attendance_date,
                status,
                selected_class,
                session["user_id"]
            )) 
        db.commit()

        flash("Attendance marked successfully!", "success")

        return redirect(url_for("teacher.dashboard"))
    return render_template(
        "teacher/mark_attendance.html",
        students=students,
        class_name=selected_class,
        attendance_map=attendance_map,
        selected_date=selected_date
    )

@attendance_bp.route("/view_attendance")
def view_attendance():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    
    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")
    selected_date = request.args.get("date", "")

    # fetch classes for dropdown 
    cursor.execute("""
        SELECT DISTINCT class_name
        FROM attendance
        ORDER BY class_name
    """)

    classes = cursor.fetchall()

    query = """
        SELECT
            a.id,
            s.name AS student_name,
            a.class_name,
            a.attendance_date,
            a.status,
            u.name AS teacher_name 
        FROM attendance a
        JOIN students s
            ON a.student_id = s.id
        JOIN users u
            ON a.marked_by = u.id
        WHERE 1=1
    """

    params = []

    # Search by student name
    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    # Filter by class
    if selected_class:
        query += " AND a.class_name=%s"
        params.append(selected_class)

    # Filter by date
    if selected_date:
        query += " AND a.attendance_date=%s"
        params.append(selected_date)

    query += """
        ORDER BY
            a.attendance_date DESC,
            s.name
    """

    cursor.execute(query, tuple(params))

    attendance = cursor.fetchall()

    return render_template(
        "admin/view_attendance.html",
        attendance=attendance,
        classes=classes,
        search=search,
        selected_class=selected_class,
        selected_date=selected_date)