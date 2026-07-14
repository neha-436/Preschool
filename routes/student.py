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
        
        
        


    