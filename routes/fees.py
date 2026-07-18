from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from db import db, cursor

fees_bp = Blueprint("fees", __name__)

@fees_bp.route("/create_fee_structure", methods=["GET", "POST"])
def create_fee_structure():

    # Login check
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    # Admin only
    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    # Fetch available classes
    cursor.execute("""
        SELECT DISTINCT class_name
        FROM timetable
        ORDER BY class_name
    """)

    classes = cursor.fetchall()

    if request.method == "POST":

        class_name = request.form["class_name"]
        total_fee = request.form["total_fee"]
        due_date = request.form["due_date"]

        # Prevent duplicate fee structure
        cursor.execute("""
            SELECT id
            FROM fee_structure
            WHERE class_name=%s
        """, (class_name,))

        if cursor.fetchone():
            flash("Fee structure already exists for this class.", "warning")
            return redirect(url_for("fees.create_fee_structure"))

        cursor.execute("""
            INSERT INTO fee_structure
            (
                class_name,
                total_fee,
                due_date
            )
            VALUES (%s, %s, %s)
        """, (
            class_name,
            total_fee,
            due_date
        ))

        db.commit()

        flash("Fee structure created successfully.", "success")

        return redirect(url_for("fees.create_fee_structure"))

    return render_template(
        "admin/create_fee_structure.html",
        classes=classes
    )

@fees_bp.route("/record_payment", methods=["GET", "POST"])
def record_payment():

    # Login check
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    # Admin only
    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    # Fetch all students
    cursor.execute("""
        SELECT
            id,
            name,
            class_name
        FROM students
        ORDER BY name
    """)
    students = cursor.fetchall()

    selected_student = request.args.get("student_id")
    fee_info = None

    # -----------------------------
    # Load Fee Information
    # -----------------------------
    if selected_student:

        cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.class_name,
                f.total_fee
            FROM students s
            JOIN fee_structure f
                ON s.class_name = f.class_name
            WHERE s.id=%s
        """, (selected_student,))

        fee_info = cursor.fetchone()

        if fee_info:

            cursor.execute("""
                SELECT
                    IFNULL(SUM(amount_paid),0) AS total_paid
                FROM fee_payment
                WHERE student_id=%s
            """, (selected_student,))

            total_paid = float(cursor.fetchone()["total_paid"])

            fee_info["paid"] = total_paid
            fee_info["remaining"] = float(fee_info["total_fee"]) - total_paid

            if total_paid == 0:
                fee_info["status"] = "Pending"
            elif total_paid < float(fee_info["total_fee"]):
                fee_info["status"] = "Partial"
            else:
                fee_info["status"] = "Paid"

    # -----------------------------
    # Record Payment
    # -----------------------------
    if request.method == "POST":

        student_id = request.form["student_id"]
        amount_paid = float(request.form["amount_paid"])
        payment_date = request.form["payment_date"]
        payment_mode = request.form["payment_mode"]

        # Get student's class
        cursor.execute("""
            SELECT class_name
            FROM students
            WHERE id=%s
        """, (student_id,))

        student = cursor.fetchone()

        class_name = student["class_name"]

        # Get fee structure
        cursor.execute("""
            SELECT total_fee
            FROM fee_structure
            WHERE class_name=%s
        """, (class_name,))

        fee = cursor.fetchone()

        if not fee:
            flash("Fee structure not found.", "danger")
            return redirect(
                url_for("fees.record_payment", student_id=student_id)
            )

        total_fee = float(fee["total_fee"])

        # Already paid
        cursor.execute("""
            SELECT
                IFNULL(SUM(amount_paid),0) AS total_paid
            FROM fee_payment
            WHERE student_id=%s
        """, (student_id,))

        total_paid = float(cursor.fetchone()["total_paid"])

        remaining = total_fee - total_paid

        # Prevent overpayment
        if amount_paid > remaining:

            flash(
                f"Payment exceeds remaining balance (₹{remaining:.2f}).",
                "danger"
            )

            return redirect(
                url_for("fees.record_payment", student_id=student_id)
            )

        new_total = total_paid + amount_paid

        if new_total == 0:
            status = "Pending"
        elif new_total < total_fee:
            status = "Partial"
        else:
            status = "Paid"

        cursor.execute("""
            INSERT INTO fee_payment
            (
                student_id,
                amount_paid,
                payment_date,
                payment_mode,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            amount_paid,
            payment_date,
            payment_mode,
            status
        ))

        db.commit()

        flash("Payment recorded successfully.", "success")

        return redirect(
            url_for("fees.record_payment", student_id=student_id)
        )

    return render_template(
        "admin/record_payment.html",
        students=students,
        fee_info=fee_info,
        selected_student=selected_student
    )

@fees_bp.route("/view_fee_payments")
def view_fee_payments():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    selected_class = request.args.get("class_name", "")
    selected_status = request.args.get("status", "")

    # Fetch available classes
    cursor.execute("""
        SELECT DISTINCT class_name
        FROM students
        ORDER BY class_name
    """)
    classes = cursor.fetchall()

    query = """
        SELECT
            s.id,
            s.name AS student_name,
            u.name AS parent_name,
            s.class_name,
            fs.total_fee,
            IFNULL(SUM(fp.amount_paid),0) AS total_paid
        FROM students s

        LEFT JOIN users u
            ON s.parent_id = u.id

        LEFT JOIN fee_structure fs
            ON s.class_name = fs.class_name

        LEFT JOIN fee_payment fp
            ON s.id = fp.student_id

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
        GROUP BY
            s.id,
            s.name,
            u.name,
            s.class_name,
            fs.total_fee
    """

    cursor.execute(query, tuple(params))

    students = cursor.fetchall()

    results = []

    for student in students:

        total_fee = float(student["total_fee"] or 0)
        total_paid = float(student["total_paid"] or 0)

        remaining = total_fee - total_paid

        if total_paid == 0:
            status = "Pending"
        elif total_paid < total_fee:
            status = "Partial"
        else:
            status = "Paid"

        if selected_status and status != selected_status:
            continue

        student["remaining"] = remaining
        student["status"] = status

        results.append(student)

    return render_template(
        "admin/view_fee_payments.html",
        students=results,
        classes=classes,
        search=search,
        selected_class=selected_class,
        selected_status=selected_status
    )

@fees_bp.route("/payment_history/<int:student_id>")
def payment_history(student_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    cursor.execute("""
        SELECT
            name,
            class_name
        FROM students
        WHERE id=%s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            amount_paid,
            payment_date,
            payment_mode,
            status
        FROM fee_payment
        WHERE student_id=%s
        ORDER BY payment_date DESC
    """, (student_id,))

    payments = cursor.fetchall()

    return render_template(
        "admin/payment_history.html",
        student=student,
        payments=payments
    )

@fees_bp.route("/parent/fees")
def parent_fee_dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if session["role"] != "parent":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    # Parent's student
    cursor.execute("""
        SELECT
            id,
            name,
            class_name
        FROM students
        WHERE parent_id=%s
    """, (session["user_id"],))

    student = cursor.fetchone()

    if not student:
        flash("No student linked to this account.", "warning")
        return redirect(url_for("parent.dashboard"))

    # Fee structure
    cursor.execute("""
        SELECT
            total_fee,
            due_date
        FROM fee_structure
        WHERE class_name=%s
    """, (student["class_name"],))

    fee = cursor.fetchone()

    if not fee:
        flash("Fee structure not found.", "warning")
        return redirect(url_for("parent.dashboard"))

    # Total paid
    cursor.execute("""
        SELECT
            IFNULL(SUM(amount_paid),0) AS total_paid
        FROM fee_payment
        WHERE student_id=%s
    """, (student["id"],))

    total_paid = float(cursor.fetchone()["total_paid"])

    total_fee = float(fee["total_fee"])
    remaining = total_fee - total_paid

    if total_paid == 0:
        status = "Pending"
    elif total_paid < total_fee:
        status = "Partial"
    else:
        status = "Paid"

    # Payment history
    cursor.execute("""
        SELECT
            payment_date,
            amount_paid,
            payment_mode,
            status
        FROM fee_payment
        WHERE student_id=%s
        ORDER BY payment_date DESC
    """, (student["id"],))

    payments = cursor.fetchall()

    return render_template(
        "parent/fee_dashboard.html",
        student=student,
        fee=fee,
        total_paid=total_paid,
        remaining=remaining,
        status=status,
        payments=payments
    )