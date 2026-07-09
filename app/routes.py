"""Routes module for defining application endpoints."""

from flask import Blueprint, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Render the index page of the application."""
    return render_template("index.html")


@main_bp.route("/health")
def health():
    """Health check endpoint returning the status of the application."""
    return jsonify({"status": "ok"})
