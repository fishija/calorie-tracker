"""Database models for the calorie tracker application."""

from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import db


class User(UserMixin, db.Model):
    """User model representing a registered user in the application.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        password_hash (str): The hashed password of the user.
        created_at (datetime): The timestamp when the user was created.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


class Goal(db.Model):
    """Goal model representing a user's nutritional goals for a specific date.

    Unique constraint is enforced on the combination of user_id and effective_date
    to ensure that a user can only have one goal per date.

    Attributes:
        id (int): The primary key for the goal.
        user_id (int): The foreign key referencing the user.
        effective_date (date): The date for which the goal is set.
        calorie_kcal (int): The target calorie intake in kilocalories.
        protein_g (int): The target protein intake in grams.
        carb_g (int): The target carbohydrate intake in grams.
        fat_g (int): The target fat intake in grams.
        created_at (datetime): The timestamp when the goal was created.
    """

    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    effective_date = db.Column(
        db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date()
    )

    calorie_kcal = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Integer, nullable=False)
    carb_g = db.Column(db.Integer, nullable=False)
    fat_g = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("user_id", "effective_date", name="uq_user_goal_date"),)


class Meal(db.Model):
    """Meal model representing a meal logged by a user.

    Attributes:
        id (int): The primary key for the meal.
        user_id (int): The foreign key referencing the user.
        logged_date (date): The date when the meal was logged.
        name (str): The name of the meal.
        calorie_kcal (int): The calorie content of the meal in kilocalories.
        protein_g (int): The protein content of the meal in grams.
        carb_g (int): The carbohydrate content of the meal in grams.
        fat_g (int): The fat content of the meal in grams.
        description (str): An optional description of the meal.
        created_at (datetime): The timestamp when the meal was created.
        photos (list[MealPhoto]): A list of associated MealPhoto objects.
    """

    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    logged_date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    calorie_kcal = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Integer, nullable=False)
    carb_g = db.Column(db.Integer, nullable=False)
    fat_g = db.Column(db.Integer, nullable=False)

    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    photos = db.relationship("MealPhoto", backref="meal", cascade="all, delete-orphan")


class MealPhoto(db.Model):
    """MealPhoto model representing a photo associated with a meal.

    Attributes:
        id (int): The primary key for the meal photo.
        meal_id (int): The foreign key referencing the associated meal.
        filename (str): The filename of the uploaded photo.
        uploaded_at (datetime): The timestamp when the photo was uploaded.
    """

    __tablename__ = "meal_photos"

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
