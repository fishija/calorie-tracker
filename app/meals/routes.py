"""Routes for managing meals and nutritional data."""

import os
from datetime import date, timedelta

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from app.db import db
from app.goals.queries import get_goal_for_date
from app.llm.estimator import estimate_meal
from app.meals.forms import MealForm
from app.meals.queries import get_meals_for_date
from app.meals.services import compute_totals
from app.meals.utils import make_unique_filename, uploaded_files_to_bytes
from app.models import Meal, MealPhoto

meals_bp = Blueprint("meals", __name__)


@meals_bp.route("/days/", methods=["GET"])
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


@meals_bp.route("/days/<date_str>/", methods=["GET", "POST"])
@login_required
def day_view(date_str=None):
    """View function for displaying meals logged on a specific date, along with
    nutritional totals and goals.

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
        "meals/day_view.html",
        selected_date=selected_date,
        prev_date=prev_date,
        next_date=next_date,
        meals=meals,
        totals=totals,
        goal=goal,
    )


@meals_bp.route("/days/<date_str>/meals/add", methods=["GET", "POST"])
@login_required
def add_meal(date_str: str):
    """View function for adding a new meal entry for a specific date.

    Returns:
        Response: The response object rendering the add meal template.
    """
    if date_str is None:
        abort(404, description="Missing date.")

    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        abort(404, description="Invalid date format. Use YYYY-MM-DD.")

    form = MealForm(logged_date=selected_date)

    if form.validate_on_submit():
        try:
            submitted_date = date.fromisoformat(form.logged_date.data)
        except ValueError:
            abort(400, description="Invalid date.")

        # Create new meal
        new_meal = Meal(
            user_id=current_user.id,
            logged_date=submitted_date,
            name=form.name.data,
            calorie_kcal=form.calorie_kcal.data,
            protein_g=form.protein_g.data,
            carb_g=form.carb_g.data,
            fat_g=form.fat_g.data,
            description=form.description.data,
        )

        # Handle photo uploads if any
        for photo in form.new_photos.data or []:
            if photo:
                # Save the photo and create a MealPhoto instance
                filename = make_unique_filename(photo.filename)
                photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                meal_photo = MealPhoto(meal=new_meal, filename=filename)
                db.session.add(meal_photo)

        db.session.add(new_meal)
        db.session.commit()
        return redirect(url_for("meals.day_view", date_str=submitted_date.isoformat()))

    return render_template("meals/add_meal.html", form=form, selected_date=selected_date)


@meals_bp.route("/meals/<int:meal_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meal(meal_id: int):
    """View function for editing an existing meal entry for a specific date.

    Args:
        meal_id (int): The ID of the meal to be edited.

    Returns:
        Response: The response object rendering the edit meal template.
    """
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    selected_date = meal.logged_date

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
                MealPhoto.id.in_(remove_ids), MealPhoto.meal_id == meal.id
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
                photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                db.session.add(MealPhoto(meal=meal, filename=filename))

        db.session.commit()
        return redirect(url_for("meals.day_view", date_str=selected_date.isoformat()))

    return render_template(
        "meals/edit_meal.html", form=form, selected_date=selected_date, meal=meal
    )


@meals_bp.route("/meals/<int:meal_id>/delete", methods=["POST"])
@login_required
def delete_meal(meal_id: int):
    """View function for deleting a meal entry for a specific date.

    Args:
        meal_id (int): The ID of the meal to be deleted.

    Returns:
        Response: The response object redirecting to the day's meal view.
    """
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    selected_date = meal.logged_date

    # Delete associated photos from the filesystem
    for photo in meal.photos:
        photo_path = os.path.join(current_app.config["UPLOAD_FOLDER"], photo.filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for("meals.day_view", date_str=selected_date.isoformat()))


@meals_bp.route("/meals/estimate_with_ai", methods=["POST"])
@login_required
def estimate_with_ai():
    """Endpoint to estimate meal nutritional content using AI based on description and
    optional images.

    Returns:
        Response: A JSON response containing the estimated nutritional content.
    """
    description = request.form.get("description", "")
    uploaded_files = request.files.getlist("new_photos")

    if not description and not uploaded_files:
        return jsonify({"error": "Description or at least one image is required."}), 400

    # Convert uploaded files to bytes for AI estimation
    image_bytes_list = uploaded_files_to_bytes(uploaded_files)

    # Call the AI estimation function
    response = estimate_meal(description, image_bytes_list)

    return jsonify(
        {
            "calorie_kcal": response.get("calorie_kcal", 0),
            "protein_g": response.get("protein_g", 0),
            "carb_g": response.get("carb_g", 0),
            "fat_g": response.get("fat_g", 0),
            "meal_summary": response.get("meal_summary", ""),
            "assumptions": response.get("assumptions", ""),
            "confidence": response.get("confidence", ""),
            "source_type": response.get("source_type", ""),
        }
    )
