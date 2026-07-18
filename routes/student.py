from flask import Flask, Blueprint, render_template, redirect, url_for, session, flash, request
from db import db, cursor

student_bp = Blueprint("student", __name__)

@student_bp.route("/register_student", methods=["GET", "POST"])
def register_student():

    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"]!="admin":
        flash("Access denied", "warning")
        return redirect(url_for("auth.login"))
    
    cursor.execute("""
            SELECT id, name
            FROM users
            WHERE role='parent'
            AND status='active'
            ORDER BY name
        """)

    parents = cursor.fetchall()

    if request.method == "POST":
        name = request.form["name"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        class_name = request.form["class_name"]
        parent_id = request.form["parent_id"]

        cursor.execute("""
            INSERT INTO students
            (name, dob, gender, class_name, parent_id)
            VALUES(%s, %s, %s, %s, %s)
        """,
        (
            name, dob, gender, class_name, parent_id
        ))

        db.commit()

        flash("Student registered successfully.","success")

        return redirect(url_for("admin.dashboard"))

    return render_template("admin/register_student.html", parents=parents)
        
        
@student_bp.route("/view_students")
def view_students():

    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"]!="admin":
        flash("Access denied", "warning")
        return redirect(url_for("auth.login"))
    
    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")

    cursor.execute("""
        SELECT DISTINCT class_name
        FROM students
        ORDER BY class_name
    """)

    classes = cursor.fetchall()
    
    query = """
        SELECT
            s.id,
            s.name,
            s.dob,
            s.gender,
            s.class_name,
            u.name AS parent_name,
            u.email AS parent_email
        FROM students s
        LEFT JOIN users u
        ON s.parent_id = u.id
        WHERE 1=1
    """
    params = []

    ## Search by name
    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    ## Filter by class
    if selected_class:
        query += " AND s.class_name = %s"
        params.append(selected_class)
    
    query += " ORDER BY s.class_name, s.name"
    cursor.execute(query, tuple(params))
    students = cursor.fetchall()

    return render_template("admin/view_students.html", students=students, classes=classes, search=search, selected_class = selected_class)

@student_bp.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin.dashboard"))
    
    cursor.execute("""
        SELECT id, name
        FROM users
        WHERE role='parent'
        AND status='active'
        ORDER BY name
    """)

    parents = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE id=%s
    """, (student_id,))

    student = cursor.fetchone()
    
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("student.view_students"))
    
    if request.method == "POST":
        name = request.form["name"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        class_name = request.form["class_name"]
        parent_id = request.form["parent_id"]

        cursor.execute("""
            UPDATE students
            SET
                name=%s,
                dob=%s,
                gender=%s,
                class_name=%s,
                parent_id=%s
            WHERE id=%s
        """, (
            name,
            dob,
            gender,
            class_name,
            parent_id,
            student_id
        ))

        db.commit()

        flash("Student updated successfully.", 'success')

        return redirect(url_for("student.view_students"))
    
    return render_template("admin/edit_student.html", student=student, parents=parents)

@student_bp.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("admin.dashboard"))

    cursor.execute("""
        DELETE FROM students
        WHERE id=%s
    """, (student_id,))

    db.commit()

    flash("Student deleted successfully.", "success")

    return redirect(url_for("student.view_students"))