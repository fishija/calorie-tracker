from flask import Blueprint, redirect, url_for, render_template, abort
from flask_login import login_required, current_user
from datetime import timedelta, date

from app.meals.queries import get_meals_for_date, compute_totals
from app.goals.queries import get_goal_for_date

meals_bp = Blueprint("meals", __name__, url_prefix="/meals")


@meals_bp.route("/", methods=["GET"])
@login_required
def index():
    return redirect(url_for("meals.day_view", date_str=date.today().isoformat()))


@meals_bp.route("/day/<date_str>/", methods=["GET", "POST"])
@login_required
def day_view(date_str=None):
    if date_str is None:
        return redirect(url_for("meals.day_view", date_str=date.today().isoformat()))
    
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        abort(404, description="Invalid date format. Use YYYY-MM-DD.")
    
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    meals = get_meals_for_date(current_user.id, selected_date)
    goal = get_goal_for_date(current_user.id, selected_date)
    totals = compute_totals(meals)

    return render_template(
        "meals/day.html", 
        selected_date=selected_date, 
        prev_date=prev_date, 
        next_date=next_date,
        meals=meals,
        totals=totals,
        goal=goal
    )


@meals_bp.route("/day/<date_str>/add", methods=["GET", "POST"])
@login_required
def add_meal(date_str):
    return redirect(url_for("meals.day_view", date_str=date_str))


@meals_bp.route("/day/<date_str>/meal/<int:meal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meal(date_str, meal_id):
    return redirect(url_for("meals.day_view", date_str=date_str))


@meals_bp.route("/day/<date_str>/meal/<int:meal_id>/delete", methods=["POST"])
@login_required
def delete_meal(date_str, meal_id):
    return redirect(url_for("meals.day_view", date_str=date_str))
