"""Routes for managing meals and nutritional data."""

from flask import Blueprint, redirect, send_from_directory, url_for, render_template, abort, current_app, request
from flask_login import login_required, current_user
from datetime import timedelta, date
import os

from app.db import db
from app.models import Meal, MealPhoto
from app.meals.forms import MealForm
from app.meals.utils import make_unique_filename
from app.meals.services import compute_totals
from app.meals.queries import get_meals_for_date
from app.goals.queries import get_goal_for_date

meals_bp = Blueprint("meals", __name__, url_prefix="/meals")


@meals_bp.route("/", methods=["GET"])
@login_required
def index():
    """Redirect to the current day's meal view."""
    return redirect(url_for("meals.day_view", date_str=date.today().isoformat()))


@meals_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename: str):
    """Serve uploaded meal photos from the server's upload directory.

    Args:
        filename (str): The name of the file to be served.

    Returns:
        Response: The response object to send the file to the client.
    """
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@meals_bp.route("/day/<date_str>/", methods=["GET", "POST"])
@login_required
def day_view(date_str=None):
    """View function for displaying meals logged on a specific date, along with nutritional totals and goals.

    Args:
        date_str (str, optional): The date string in YYYY-MM-DD format. Defaults to None.

    Returns:
        Response: The response object rendering the meal view template.
    """
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
    """View function for adding a new meal entry for a specific date.

    Args:
        date_str (str): The date string in YYYY-MM-DD format.

    Returns:
        Response: The response object rendering the add meal template.
    """
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        abort(404, description="Invalid date format. Use YYYY-MM-DD.")

    form = MealForm()

    if form.validate_on_submit():
        # Create new meal
        new_meal = Meal(
            user_id=current_user.id,
            logged_date=selected_date,
            name=form.name.data,
            calorie_kcal=form.calorie_kcal.data,
            protein_g=form.protein_g.data,
            carb_g=form.carb_g.data,
            fat_g=form.fat_g.data,
            description=form.description.data
        )

        # Handle photo uploads if any
        for photo in form.new_photos.data or []:
            if photo:
                # Save the photo and create a MealPhoto instance
                filename = make_unique_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                meal_photo = MealPhoto(meal=new_meal, filename=filename)
                db.session.add(meal_photo)

        db.session.add(new_meal)
        db.session.commit()
        return redirect(url_for("meals.day_view", date_str=selected_date.isoformat()))

    return render_template("meals/add_meal.html", form=form, selected_date=selected_date)


@meals_bp.route("/day/<date_str>/meal/<int:meal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meal(date_str: str, meal_id: int):
    """View function for editing an existing meal entry for a specific date.

    Args:
        date_str (str): The date string in YYYY-MM-DD format.
        meal_id (int): The ID of the meal to be edited.

    Returns:
        Response: The response object rendering the edit meal template.
    """
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        abort(404, description="Invalid date format. Use YYYY-MM-DD.")

    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()

    form = MealForm(obj=meal)

    if form.validate_on_submit():
        meal.name = form.name.data
        meal.calorie_kcal = form.calorie_kcal.data
        meal.protein_g = form.protein_g.data
        meal.carb_g = form.carb_g.data
        meal.fat_g = form.fat_g.data
        meal.description = form.description.data

        # remove photos if any
        remove_ids = request.form.getlist("remove_photos", type=int)
        if remove_ids:
            photos_to_remove = MealPhoto.query.filter(
                MealPhoto.id.in_(remove_ids), 
                MealPhoto.meal_id == meal.id
            ).all()
            for photo in photos_to_remove:
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], photo.filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                db.session.delete(photo)

        # add new photos if any
        for photo in form.new_photos.data or []:
            if photo and photo.filename:
                filename = make_unique_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                db.session.add(MealPhoto(meal=meal, filename=filename))

        db.session.commit()
        return redirect(url_for("meals.day_view", date_str=selected_date.isoformat()))
    
    return render_template("meals/edit_meal.html", form=form, selected_date=selected_date, meal=meal)


@meals_bp.route("/day/<date_str>/meal/<int:meal_id>/delete", methods=["POST"])
@login_required
def delete_meal(date_str: str, meal_id: int):
    """View function for deleting a meal entry for a specific date.

    Args:
        date_str (str): The date string in YYYY-MM-DD format.
        meal_id (int): The ID of the meal to be deleted.

    Returns:
        Response: The response object redirecting to the day's meal view.
    """
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        abort(404, description="Invalid date format. Use YYYY-MM-DD.")

    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    
    # Delete associated photos from the filesystem
    for photo in meal.photos:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for("meals.day_view", date_str=selected_date.isoformat()))
