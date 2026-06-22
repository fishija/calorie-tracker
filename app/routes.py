from flask import Blueprint, jsonify

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return jsonify({"message": "hello world"})


@main.route("/health")
def health():
    return jsonify({"status": "ok"})
