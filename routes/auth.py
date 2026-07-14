from flask import Blueprint, render_template, redirect, url_for, flash, session, request

from werkzeug.security import check_password_hash

from db import cursor

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        selected_role = request.form["role"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s", (email,)
        )

        user = cursor.fetchone()

        if not user:
            flash("Invalid email", "danger")
            return redirect(url_for("auth.login"))
        
        if not check_password_hash(user["password"], password):
            flash("Incorrect Password", "danger")
            return redirect(url_for("auth.login")) 
        
        if user["role"] != selected_role:
            flash("Selected role does not match your account.", "danger")
            return redirect(url_for("auth.login"))
        
        if user["status"] != "active":
            flash("Account pending approval", "danger")
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

@auth_bp.route("/flash-test")
def flash_test():
    flash("Flash is working!", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
def logout():
    return redirect(url_for("auth.login"))