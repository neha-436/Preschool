from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def dashboard():
    return "<h1>Admin Dashboard</h1>"