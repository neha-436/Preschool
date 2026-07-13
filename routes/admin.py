from flask import Blueprint, session, redirect, url_for, render_template

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("auth.login"))

    return render_template("admin/dashboard.html")