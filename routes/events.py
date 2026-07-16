from flask import Flask, render_template, redirect, session, flash, url_for, Blueprint, request
from db import db, cursor

events_bp = Blueprint("events", __name__)

@events_bp.route("/post_event", methods=["GET", "POST"])
def post_event():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    
    cursor.execute("""
        SELECT DISTINCT class_name
        FROM timetable
        ORDER BY class_name
    """)
    classes = cursor.fetchall()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        event_date = request.form["event_date"]
        target_class = request.form["target_class"]

        if target_class == "":
            target_class = None

        cursor.execute("""
            INSERT INTO events
            (title, description, event_date, target_class)
            VALUES (%s, %s, %s, %s)
        """, (
            title,
            description,
            event_date,
            target_class
        ))

        db.commit()

        flash("Event posted successfully!", "success")

        return redirect(url_for("events.view_events"))

    return render_template("admin/post_event.html", classes = classes)


@events_bp.route("/view_events")
def view_events():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    role = session["role"]

    #---Admin---
    if role == "admin":
        cursor.execute("""
            SELECT *
            FROM events
            ORDER BY event_date DESC
        """)

        events = cursor.fetchall()

    #---Teacher---
    elif role == "teacher":
        cursor.execute("""
            SELECT class_assigned
            FROM teachers
            WHERE user_id=%s
        """, (session["user_id"],))

        teacher = cursor.fetchone()

        cursor.execute("""
            SELECT *
            FROM events
            WHERE target_class=%s
                       OR target_class IS NULL
            ORDER BY event_date DESC
        """, (teacher["class_assigned"],))

        events = cursor.fetchall()
    
    else:
        cursor.execute("""
            SELECT class_name
            FROM students
            WHERE parent_id=%s
        """, (session["user_id"],))

        student = cursor.fetchone()

        if student:
            cursor.execute("""
            SELECT *
            FROM events
            WHERE target_class=%s
                       OR target_class IS NULL
            ORDER BY event_date DESC
            """, (student["class_name"],))

            events = cursor.fetchall()
        
        else:
            events = []

    return render_template("events/view_events.html", events = events)

        



