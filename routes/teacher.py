from flask import render_template, redirect, request, flash, Blueprint, url_for
from werkzeug.security import generate_password_hash

from db import db, cursor

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route("/register_teacher", methods=["GET", "POST"])
def register_teacher():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        assigned_class = request.form["assigned_class"]

        # check duplicate email
        cursor.execute(
            "SELECT id FROM users WHERE email=%s", (email,)
        )
        if cursor.fetchone():
            flash("Email already exits", "danger")
            return redirect("/register_teacher")
        
        # hashing password before storing in db
        hashed_pass = generate_password_hash(password)

        cursor.execute(
            """INSERT INTO users (name, email, password, role, status)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                name, email, hashed_pass, "teacher",
                "active"
            )
        )

        db.commit()
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO teachers
            (user_id, class_assigned)
            VALUES (%s, %s)
        """, (
                user_id, assigned_class
            )
        )
        db.commit()

        flash("Teacher Registered Successfully!", "success")

        return redirect(url_for("teacher.register_teacher"))

    return render_template("register_teacher.html")

@teacher_bp.route("/teacher/dashboard")
def dashboard():
    return "<h1>Teacher Dashboard</h1>"