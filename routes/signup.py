from werkzeug.security import generate_password_hash
from flask import render_template, request, redirect, url_for, flash, Blueprint
from db import db, cursor

signup_bp = Blueprint("signup", __name__)

@signup_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        if cursor.fetchone():
            flash("Email already exists.", "danger")
            return redirect(url_for("signup.signup"))
        
        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users(name, email, password, role, status) VALUES(%s, %s, %s, %s, %s)
        """, (
            name, email, hashed_password, "parent", "pending"
        ))

        db.commit()

        flash("Account cretaed successfully. Please wait for admin approval.", "success")

        return redirect(url_for("auth.login"))
    
    return render_template("auth/signup.html")