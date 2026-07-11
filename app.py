from flask import Flask, redirect, url_for

from routes.teacher import teacher_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.parent import parent_bp

app = Flask(__name__)
app.secret_key = "secretkey"

app.register_blueprint(teacher_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(parent_bp)

@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)