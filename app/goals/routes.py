from datetime import datetime, timezone, timedelta

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from app.db import db
from app.models import Goal
from app.goals.forms import GoalForm

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


def _today_utc_range() -> tuple[datetime, datetime]:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def _get_todays_goal(user_id: int) -> Goal | None:
    start, end = _today_utc_range()
    return (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date >= start,
            Goal.effective_date < end
        ).first()
    )


@goals_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    todays_goal = _get_todays_goal(user_id=current_user.id)
    form = GoalForm()

    if form.validate_on_submit():
        if todays_goal:
            # Update existing goal
            todays_goal.calorie_kcal = form.calorie_kcal.data
            todays_goal.protein_g = form.protein_g.data
            todays_goal.carb_g = form.carb_g.data
            todays_goal.fat_g = form.fat_g.data
            flash("Today's goal has been updated.", "success")
        else:
            # Create new goal
            new_goal = Goal(
                user_id=current_user.id,
                effective_date=datetime.now(timezone.utc),
                calorie_kcal=form.calorie_kcal.data,
                protein_g=form.protein_g.data,
                carb_g=form.carb_g.data,
                fat_g=form.fat_g.data
            )
            db.session.add(new_goal)
            flash("New goal has been added, effective today.", "success")

        db.session.commit()
        return redirect(url_for("goals.index"))
    
    history = (
        Goal.query.filter(Goal.user_id == current_user.id)
        .order_by(Goal.effective_date.desc())
        .all()
    )

    return render_template("goals/index.html", form=form, todays_goal=todays_goal, history=history)
