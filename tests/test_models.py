from datetime import date, datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Goal, Meal, MealPhoto, User


class TestUserModel:
    def test_password_hashing(self, db):
        user = User(username="chef_clara", email="clara@example.com")
        user.set_password("secure_password_123")

        assert user.password_hash != "secure_password_123"
        assert user.check_password("secure_password_123") is True
        assert user.check_password("wrong_password") is False

    def test_duplicate_username_raises_error(self, db, make_user):
        make_user(username="duplicate_user", email="user1@example.com")

        second_user = User(username="duplicate_user", email="user2@example.com")
        second_user.set_password("password123")
        db.session.add(second_user)

        with pytest.raises(IntegrityError):
            db.session.commit()


class TestGoalModel:
    def test_default_date(self, db, make_user):
        """Test that a goal defaults to the current UTC date if not specified."""
        user = make_user()
        goal = Goal(user_id=user.id, calorie_kcal=2000, protein_g=150, carb_g=200, fat_g=65)
        db.session.add(goal)
        db.session.commit()

        assert goal.effective_date == datetime.now(timezone.utc).date()

    def test_unique_user_date_constraint(self, db, make_user):
        user = make_user()
        specific_date = date(2026, 7, 13)

        goal1 = Goal(
            user_id=user.id,
            effective_date=specific_date,
            calorie_kcal=2000,
            protein_g=150,
            carb_g=200,
            fat_g=65,
        )
        db.session.add(goal1)
        db.session.commit()

        goal2 = Goal(
            user_id=user.id,
            effective_date=specific_date,
            calorie_kcal=1800,
            protein_g=130,
            carb_g=180,
            fat_g=60,
        )
        db.session.add(goal2)

        with pytest.raises(IntegrityError):
            db.session.commit()


class TestMealAndPhotoRelationships:
    def test_meal_and_photo_cascade_delete(self, db, make_user):
        user = make_user()
        meal = Meal(
            user_id=user.id,
            logged_date=date(2026, 7, 13),
            name="Avocado Toast",
            calorie_kcal=350,
            protein_g=12,
            carb_g=30,
            fat_g=22,
        )
        db.session.add(meal)
        db.session.commit()

        photo1 = MealPhoto(meal_id=meal.id, filename="toast1.jpg")
        photo2 = MealPhoto(meal_id=meal.id, filename="toast2.jpg")
        db.session.add_all([photo1, photo2])
        db.session.commit()

        assert len(meal.photos) == 2

        db.session.delete(meal)
        db.session.commit()

        assert db.session.get(MealPhoto, photo1.id) is None
        assert db.session.get(MealPhoto, photo2.id) is None

    def test_meal_photo_orphan_removal(self, db, make_user):
        user = make_user()
        meal = Meal(
            user_id=user.id,
            logged_date=date(2026, 7, 13),
            name="Lunch",
            calorie_kcal=500,
            protein_g=30,
            carb_g=50,
            fat_g=15,
        )
        db.session.add(meal)
        db.session.commit()

        photo = MealPhoto(meal_id=meal.id, filename="lunch.jpg")
        db.session.add(photo)
        db.session.commit()

        meal.photos.remove(photo)
        db.session.commit()

        assert db.session.get(MealPhoto, photo.id) is None
