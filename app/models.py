from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app.db import db


class User(UserMixin, db.Model):
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
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    effective_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    calorie_kcal = db.Column(db.Integer, nullable=False)
    protein_g = db.Column(db.Integer, nullable=False)
    carb_g = db.Column(db.Integer, nullable=False)
    fat_g = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Meal(db.Model):
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
    __tablename__ = "meal_photos"

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
