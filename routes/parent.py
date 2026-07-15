from flask import Blueprint, session, redirect, flash, url_for, render_template

parent_bp = Blueprint("parent", __name__)


@parent_bp.route("/parent/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "parent":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("parent/dashboard.html")