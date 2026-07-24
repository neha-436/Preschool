from flask import Flask, Blueprint, session, redirect, request, render_template, flash, url_for

from db import db, cursor

timetable_bp = Blueprint("timetable", __name__)

@timetable_bp.route("/create_timetable", methods=["GET", "POST"])
def create_timetable():
    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))
    
    if session["role"] != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    cursor.execute("""
        SELECT DISTINCT class_name
        FROM attendance
        ORDER BY class_name
        """)

    classes = cursor.fetchall()
    selected_class = ""
    
    if request.method == "POST":
        selected_class = request.form["class_name"]
        # class_name = request.form["class_name"]
        day = request.form["day"]

        period1 = request.form["period1"]
        period2 = request.form["period2"]
        period3 = request.form["period3"]
        period4 = request.form["period4"]
        period5 = request.form["period5"]
        period6 = request.form["period6"]

        #preventing duplicate timetable
        cursor.execute("""
            SELECT id
            FROM timetable
            WHERE class_name=%s AND day=%s
        """, (selected_class, day))

        if cursor.fetchone():
            flash("Timetable already exists for this class and day.", "warning")
            return redirect(url_for("timetable.create_timetable"))
        
        cursor.execute("""
            INSERT INTO timetable
            (class_name, day, period1, period2, period3, period4, period5, period6)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        """, (selected_class, day, period1, period2, period3, period4, period5, period6))

        db.commit()

        flash("Timetable created successfully", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/create_timetable.html", classes=classes, selected_class=selected_class)

@timetable_bp.route("/view_timetable")
def view_timetable():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))
    
    role = session["role"]

    #---Admin---
    if role == "admin":

        selected_class = request.args.get("class_name")

        cursor.execute("""
            SELECT DISTINCT class_name
            FROM timetable
            ORDER BY class_name
        """)
        classes = cursor.fetchall()

        if selected_class:

            cursor.execute("""
                SELECT *
                FROM timetable
                WHERE class_name=%s
                ORDER BY FIELD(day,
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday')
            """, (selected_class,))

        else:

            cursor.execute("""
                SELECT *
                FROM timetable
                ORDER BY class_name,
                FIELD(day,
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday')
            """)

        timetable = cursor.fetchall()

    #---Teacher---
    elif role == "teacher":

        classes = []
        selected_class = None

        cursor.execute("""
            SELECT class_assigned
            FROM teachers
            WHERE user_id=%s
        """, (session["user_id"],))


        teacher = cursor.fetchone()

        cursor.execute("""
            SELECT *
            FROM timetable
            WHERE class_name=%s
            ORDER BY FIELD(day,
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday')
        """, (teacher["class_assigned"],))

        timetable = cursor.fetchall()

    #---Parent---

    else:

        classes = []
        selected_class = None

        cursor.execute("""
            SELECT class_name
            FROM students
            WHERE parent_id=%s
            LIMIT 1
        """, (session["user_id"],))

        student = cursor.fetchone()

        if student:
            cursor.execute("""
                SELECT *
                    FROM timetable
                    WHERE class_name=%s
                    ORDER BY FIELD(day,
                        'Monday',
                        'Tuesday',
                        'Wednesday',
                        'Thursday',
                        'Friday')
            """, (student["class_name"],))

            timetable = cursor.fetchall()

        else:
            timetable = []
    
    return render_template("timetable/view_timetable.html", timetable=timetable, classes=classes, selected_class = selected_class)