"""Tests for goals module."""

from datetime import date, timedelta

import pytest

from app.goals.forms import GoalForm
from app.goals.queries import get_goal_for_date, get_todays_goal
from app.models import Goal


@pytest.fixture
def make_goal(db):
    """Factory fixture for creating a goal quickly inside a test.

    Returns a function rather than a goal directly, so each test can
    call it with whatever user_id/effective_date/calorie_kcal/protein_g/carb_g/fat_g it needs:

        def test_something(make_goal):
            user = make_user()
            goal = make_goal(
                user_id=user.id,
                effective_date=date.today(),
                calorie_kcal=2000,
                protein_g=150,
                carb_g=250,
                fat_g=70
            )
    """

    def _make_goal(
        user_id,
        effective_date=date.today(),
        calorie_kcal=2000,
        protein_g=150,
        carb_g=250,
        fat_g=70,
    ):
        goal = Goal(
            user_id=user_id,
            effective_date=effective_date,
            calorie_kcal=calorie_kcal,
            protein_g=protein_g,
            carb_g=carb_g,
            fat_g=fat_g,
        )
        db.session.add(goal)
        db.session.commit()
        return goal

    return _make_goal


class TestGoalForm:
    def test_accepts_valid_data(self, app):
        with app.test_request_context():
            form = GoalForm(
                data={
                    "calorie_kcal": 2000,
                    "protein_g": 150,
                    "carb_g": 250,
                    "fat_g": 70,
                }
            )
            assert form.validate() is True

    def test_rejects_negative_values(self, app):
        with app.test_request_context():
            form = GoalForm(
                data={
                    "calorie_kcal": -2000,
                    "protein_g": -150,
                    "carb_g": -250,
                    "fat_g": -70,
                }
            )
            assert form.validate() is False
            assert "calorie_kcal" in form.errors
            assert "protein_g" in form.errors
            assert "carb_g" in form.errors
            assert "fat_g" in form.errors

    def test_rejects_excessive_values(self, app):
        with app.test_request_context():
            form = GoalForm(
                data={
                    "calorie_kcal": 20000,
                    "protein_g": 1500,
                    "carb_g": 2500,
                    "fat_g": 1100,
                }
            )
            assert form.validate() is False
            assert "calorie_kcal" in form.errors
            assert "protein_g" in form.errors
            assert "carb_g" in form.errors
            assert "fat_g" in form.errors

    def test_rejects_missing_values(self, app):
        with app.test_request_context():
            form = GoalForm(
                data={
                    "calorie_kcal": "",
                    "protein_g": "",
                    "carb_g": "",
                    "fat_g": "",
                }
            )
            assert form.validate() is False
            assert "calorie_kcal" in form.errors
            assert "protein_g" in form.errors
            assert "carb_g" in form.errors
            assert "fat_g" in form.errors


class TestGoalQueries:
    def test_get_todays_goal_returns_goal_if_exists(self, db, make_user, make_goal):
        user = make_user()
        # Create a goal for today
        _ = make_goal(
            user_id=user.id,
        )
        db.session.commit()

        retrieved_goal = get_todays_goal(user.id)
        assert retrieved_goal is not None
        assert retrieved_goal.calorie_kcal == 2000

    def test_get_goal_for_date_returns_latest_goal_before_date(self, db, make_user, make_goal):
        user = make_user()
        # Create two goals: one for yesterday and one for today
        yesterday_goal = make_goal(
            user_id=user.id,
            effective_date=date.today() - timedelta(days=1),
            calorie_kcal=1800,
        )
        today_goal = make_goal(
            user_id=user.id,
            effective_date=date.today(),
            calorie_kcal=2000,
        )
        db.session.add(yesterday_goal)
        db.session.add(today_goal)
        db.session.commit()

        retrieved_goal = get_goal_for_date(user.id, date.today())
        assert retrieved_goal is not None
        assert retrieved_goal.calorie_kcal == 2000

    def test_get_goal_for_date_returns_earliest_future_goal_if_no_prior_goal(
        self, db, make_user, make_goal
    ):
        user = make_user()
        # Create a goal for tomorrow
        tomorrow_goal = make_goal(
            user_id=user.id,
            effective_date=date.today() + timedelta(days=1),
            calorie_kcal=2200,
        )
        db.session.add(tomorrow_goal)
        db.session.commit()

        retrieved_goal = get_goal_for_date(user.id, date.today())
        assert retrieved_goal is not None
        assert retrieved_goal.calorie_kcal == 2200

    def test_get_goal_for_date_returns_goal_between_prior_and_future_goals(
        self, db, make_user, make_goal
    ):
        user = make_user()
        # Create a goal for yesterday and a goal for tomorrow
        yesterday_goal = make_goal(
            user_id=user.id,
            effective_date=date.today() - timedelta(days=1),
            calorie_kcal=1800,
        )
        tomorrow_goal = make_goal(
            user_id=user.id,
            effective_date=date.today() + timedelta(days=1),
            calorie_kcal=2200,
        )
        db.session.add(yesterday_goal)
        db.session.add(tomorrow_goal)
        db.session.commit()

        retrieved_goal = get_goal_for_date(user.id, date.today())
        assert retrieved_goal is not None
        assert retrieved_goal.calorie_kcal == 1800  # Should return the latest goal before today

    def test_get_todays_goal_returns_none_if_no_goal(self, make_user):
        user = make_user()
        goal = get_todays_goal(user.id)
        assert goal is None

    def test_get_goal_for_date_returns_none_if_no_goals(self, make_user):
        user = make_user()
        goal = get_goal_for_date(user.id, date.today())
        assert goal is None


class TestGoalRoutes:
    def test_index_route_requires_login(self, client):
        response = client.get("/goals/")
        assert response.status_code == 302  # Redirect to login

    def test_index_route_displays_form_and_history(self, client, make_user, make_goal):
        user = make_user()
        # Log in the user
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        # Create a goal for today
        make_goal(user_id=user.id)

        response = client.get("/goals/")
        assert response.status_code == 200

    def test_index_route_updates_existing_goal(self, client, make_user, make_goal):
        user = make_user()
        # Log in the user
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        # Create a goal for today
        make_goal(user_id=user.id)

        response = client.post(
            "/goals/",
            data={
                "calorie_kcal": 2500,
                "protein_g": 180,
                "carb_g": 300,
                "fat_g": 80,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        updated_goal = get_todays_goal(user.id)
        assert updated_goal.calorie_kcal == 2500

    def test_index_route_creates_new_goal_if_none_exists(self, client, make_user):
        user = make_user()
        # Log in the user
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            "/goals/",
            data={
                "calorie_kcal": 2500,
                "protein_g": 180,
                "carb_g": 300,
                "fat_g": 80,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"New goal has been added, effective today." in response.data

        new_goal = get_todays_goal(user.id)
        assert new_goal is not None
        assert new_goal.calorie_kcal == 2500

    def test_index_route_rejects_invalid_data(self, client, make_user):
        user = make_user()
        # Log in the user
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            "/goals/",
            data={
                "calorie_kcal": -2500,  # Invalid negative value
                "protein_g": -180,
                "carb_g": -300,
                "fat_g": -80,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert get_todays_goal(user.id) is None  # No goal should be created or updated
