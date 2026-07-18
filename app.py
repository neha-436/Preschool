from flask import Flask, redirect, url_for

from routes.teacher import teacher_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.parent import parent_bp
from routes.signup import signup_bp
from routes.student import student_bp
from routes.timetable import timetable_bp
from routes.events import events_bp
from routes.attendance import attendance_bp
from routes.report import report_bp
from routes.fees import fees_bp

app = Flask(__name__)
app.secret_key = "secretkey"

app.register_blueprint(teacher_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(parent_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(student_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(events_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(report_bp)
app.register_blueprint(fees_bp)

@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)