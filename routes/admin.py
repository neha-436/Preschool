from flask import Blueprint, session, redirect, url_for, render_template, flash
from db import cursor, db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/dashboard")
def dashboard():

    # Check if user is logged in
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    # Allow only admins
    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    # -----------------------------
    # Pending Parent Requests
    # -----------------------------
    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE role = 'parent'
        AND status = 'pending'
    """)
    pending_parents = cursor.fetchall()

    # -----------------------------
    # Pending Parent Count
    # -----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'parent'
        AND status = 'pending'
    """)
    pending_count = cursor.fetchone()["total"]

    # -----------------------------
    # Teacher Count
    # -----------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'teacher'
    """)
    teacher_count = cursor.fetchone()["total"]

    # -----------------------------
    # Student Count
    # -----------------------------
    # Replace with actual query once students table is created
    student_count = 0

    # Uncomment this after creating students table

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM students
    """)
    student_count = cursor.fetchone()["total"]

    return render_template(
        "admin/dashboard.html",
        parents=pending_parents,
        pending_count=pending_count,
        teacher_count=teacher_count,
        student_count=student_count
    )

@admin_bp.route("/approve_parent/<int:user_id>", methods=["POST"])
def approve_parent(user_id):

    cursor.execute("""
        UPDATE users
        SET status = 'active'
        WHERE id=%s
    """, (user_id,))

    db.commit()

    flash("Parent approved successfully!", "success")

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/reject_parent/<int:user_id>", methods=["POST"])
def reject_parent(user_id):

    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (user_id,)
    )

    db.commit()

    flash("Request rejected.", "danger")

    return redirect(url_for("admin.dashboard"))

