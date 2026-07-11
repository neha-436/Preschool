from flask import Blueprint

parent_bp = Blueprint("parent", __name__)


@parent_bp.route("/parent/dashboard")
def dashboard():
    return "<h1>Parent Dashboard</h1>"