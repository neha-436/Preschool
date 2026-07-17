from flask import Blueprint, session, redirect, url_for
from flask import flash, request, Response
from db import cursor
import csv
import io
from fpdf import FPDF

report_bp = Blueprint("report", __name__)

@report_bp.route("/export/students/csv")
def export_students_csv():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")

    query = """
        SELECT
            s.name,
            s.class_name,
            s.gender,
            s.dob,
            u.name AS parent_name,
            u.email AS parent_email

        FROM students s

        LEFT JOIN users u
            ON s.parent_id = u.id

        WHERE 1=1
    """

    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    if selected_class:
        query += " AND s.class_name=%s"
        params.append(selected_class)

    query += """
        ORDER BY
        s.class_name,
        s.name
    """

    cursor.execute(query, tuple(params))

    students = cursor.fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Student Name",
        "Class",
        "Gender",
        "DOB",
        "Parent",
        "Parent Email"
    ])

    for student in students:

        writer.writerow([
            student["name"],
            student["class_name"],
            student["gender"],
            student["dob"],
            student["parent_name"],
            student["parent_email"]
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=students_report.csv"
        }
    )

@report_bp.route("/export/attendance/csv")
def export_attendance_csv():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")
    selected_date = request.args.get("date", "")

    query = """
        SELECT
            s.name AS student_name,
            a.class_name,
            a.attendance_date,
            a.status,
            u.name AS teacher_name
        FROM attendance a
        JOIN students s
            ON a.student_id = s.id
        JOIN users u
            ON a.marked_by = u.id
        WHERE 1=1
    """

    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    if selected_class:
        query += " AND a.class_name=%s"
        params.append(selected_class)

    if selected_date:
        query += " AND a.attendance_date=%s"
        params.append(selected_date)

    query += """
        ORDER BY
            a.attendance_date DESC,
            s.name
    """

    cursor.execute(query, tuple(params))

    records = cursor.fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Student",
        "Class",
        "Date",
        "Status",
        "Marked By"
    ])

    for row in records:

        writer.writerow([
            row["student_name"],
            row["class_name"],
            row["attendance_date"],
            row["status"],
            row["teacher_name"]
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance_report.csv"
        }
    )

@report_bp.route("/export/timetable/pdf")
def export_timetable_pdf():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    selected_class = request.args.get("class_name", "")

    if not selected_class:
        flash("Please select a class.", "warning")
        return redirect(url_for("timetable.view_timetable"))

    cursor.execute("""
        SELECT *
        FROM timetable
        WHERE class_name=%s
        ORDER BY
            FIELD(day,
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday')
    """, (selected_class,))

    timetable = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "School Timetable", ln=True, align="C")

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Class : {selected_class}", ln=True)

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)

    headers = [
        "Day",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6"
    ]

    widths = [28, 26, 26, 26, 26, 26, 26]

    for header, width in zip(headers, widths):
        pdf.cell(width, 10, header, border=1, align="C")

    pdf.ln()

    pdf.set_font("Helvetica", "", 9)

    for row in timetable:

        pdf.cell(28,10,row["day"],1)

        pdf.cell(26,10,row["period1"],1)

        pdf.cell(26,10,row["period2"],1)

        pdf.cell(26,10,row["period3"],1)

        pdf.cell(26,10,row["period4"],1)

        pdf.cell(26,10,row["period5"],1)

        pdf.cell(26,10,row["period6"],1)

        pdf.ln()

    pdf_bytes = pdf.output(dest="S")

    return Response(
        bytes(pdf_bytes),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=timetable_{selected_class}.pdf"
        }
    )

@report_bp.route("/export/students/pdf")
def export_students_pdf():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")

    query = """
        SELECT
            s.name,
            s.class_name,
            s.gender,
            s.dob,
            u.name AS parent_name

        FROM students s

        LEFT JOIN users u
        ON s.parent_id=u.id

        WHERE 1=1
    """

    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    if selected_class:
        query += " AND s.class_name=%s"
        params.append(selected_class)

    query += """
        ORDER BY
        s.class_name,
        s.name
    """

    cursor.execute(query, tuple(params))

    students = cursor.fetchall()

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(0, 10, "Students Report", ln=True, align="C")

    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)

    pdf.cell(
        0,
        8,
        f"Class : {selected_class if selected_class else 'All'}",
        ln=True
    )

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)

    headers = [
        "Student",
        "Class",
        "Gender",
        "DOB",
        "Parent"
    ]

    widths = [50,25,25,40,50]

    for h, w in zip(headers, widths):
        pdf.cell(w, 10, h, 1, align="C")

    pdf.ln()

    pdf.set_font("Helvetica", "", 9)

    for student in students:

        pdf.cell(50,10,student["name"],1)

        pdf.cell(25,10,student["class_name"],1)

        pdf.cell(25,10,student["gender"],1)

        pdf.cell(40,10,str(student["dob"]),1)

        pdf.cell(50,10,student["parent_name"],1)

        pdf.ln()

    pdf_bytes = pdf.output()

    return Response(
        bytes(pdf_bytes),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=students_report.pdf"
        }
    )

@report_bp.route("/export/attendance/pdf")
def export_attendance_pdf():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")
    selected_date = request.args.get("date", "")

    query = """
        SELECT
            s.name AS student_name,
            a.class_name,
            a.attendance_date,
            a.status,
            u.name AS teacher_name

        FROM attendance a

        JOIN students s
        ON a.student_id=s.id

        JOIN users u
        ON a.marked_by=u.id

        WHERE 1=1
    """

    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    if selected_class:
        query += " AND a.class_name=%s"
        params.append(selected_class)

    if selected_date:
        query += " AND a.attendance_date=%s"
        params.append(selected_date)

    query += """
        ORDER BY
        a.attendance_date DESC,
        s.name
    """

    cursor.execute(query, tuple(params))

    attendance = cursor.fetchall()

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(0,10,"Attendance Report",ln=True,align="C")

    pdf.ln(5)

    pdf.set_font("Helvetica","B",9)

    headers = [
        "Student",
        "Class",
        "Date",
        "Status",
        "Teacher"
    ]

    widths = [50,25,35,30,50]

    for h,w in zip(headers,widths):
        pdf.cell(w,10,h,1,align="C")

    pdf.ln()

    pdf.set_font("Helvetica","",8)

    for row in attendance:

        pdf.cell(50,10,row["student_name"],1)

        pdf.cell(25,10,row["class_name"],1)

        pdf.cell(35,10,str(row["attendance_date"]),1)

        pdf.cell(30,10,row["status"],1)

        pdf.cell(50,10,row["teacher_name"],1)

        pdf.ln()

    pdf_bytes = pdf.output()

    return Response(
        bytes(pdf_bytes),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance_report.pdf"
        }
    )