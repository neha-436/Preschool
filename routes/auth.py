from flask import Blueprint, render_template, redirect, url_for, flash, session, request

from werkzeug.security import check_password_hash

from db import cursor

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s", (email,)
        )

        user = cursor.fetchone()

        if not user:
            flash("Invalid email")
            return redirect(url_for("auth.login"))
        
        if not check_password_hash(user["password"], password):
            flash("Incorrect Password")
            return redirect(url_for("auth.login")) 
        
        if user["status"] != "active":
            flash("Account pending approval")
            return redirect(url_for("auth.login"))
        
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect(url_for("admin.dashboard"))
        elif user["role"] == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("parent.dashboard"))
        
    return render_template("auth/login.html")