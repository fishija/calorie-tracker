"""Tests for meals module."""

import base64
import io
from datetime import date

import pytest
from werkzeug.datastructures import FileStorage

from app.meals.forms import MealForm
from app.meals.queries import get_meals_for_date
from app.meals.routes import make_unique_filename, uploaded_files_to_bytes
from app.meals.services import compute_totals
from app.models import Meal


@pytest.fixture
def make_meal(db):
    """Factory fixture for creating a meal quickly inside a test.

    Returns a function rather than a meal directly, so each test can
    call it with whatever user_id/logged_date/name/calorie_kcal/protein_g/carb_g/fat_g/description
    it needs:

        def test_something(make_meal):
            user = make_user()
            meal = make_meal(
                user_id=user.id,
                logged_date=date.today(),
                name="Breakfast",
                calorie_kcal=300,
                protein_g=20,
                carb_g=40,
                fat_g=10,
                description="A healthy breakfast.",
            )
    """

    def _make_meal(
        user_id,
        logged_date=date.today(),
        name="Breakfast",
        calorie_kcal=300,
        protein_g=20,
        carb_g=40,
        fat_g=10,
        description="A healthy breakfast.",
    ):
        meal = Meal(
            user_id=user_id,
            logged_date=logged_date,
            name=name,
            calorie_kcal=calorie_kcal,
            protein_g=protein_g,
            carb_g=carb_g,
            fat_g=fat_g,
            description=description,
        )
        db.session.add(meal)
        db.session.commit()
        return meal

    return _make_meal


class TestMealForm:
    def test_meal_form_valid_data(self, app):
        with app.test_request_context():
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="Test Meal",
                calorie_kcal=500,
                protein_g=30,
                carb_g=50,
                fat_g=20,
                description="A test meal.",
            )
            assert form.validate() is True

    def test_meal_form_valid_data_with_photos(self, app):
        with app.test_request_context():
            fake_image = FileStorage(
                stream=io.BytesIO(b"fake image bytes"),
                filename="photo.jpg",
                content_type="image/jpeg",
            )
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="Test Meal",
                calorie_kcal=500,
                protein_g=30,
                carb_g=50,
                fat_g=20,
                description="A test meal.",
                new_photos=[fake_image],
            )
            assert form.validate() is True

    def test_meal_form_invalid_data(self, app):
        with app.test_request_context():
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="",
                calorie_kcal=-100,  # Invalid negative calories
                protein_g=-10,  # Invalid negative protein
                carb_g=-20,  # Invalid negative carbs
                fat_g=-5,  # Invalid negative fats
                description="",
            )
        assert form.validate() is False

    def test_meal_form_missing_required_fields(self, app):
        with app.test_request_context():
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="",
                calorie_kcal=None,
                protein_g=None,
                carb_g=None,
                fat_g=None,
                description="",
            )
            assert form.validate() is False

    def test_rejects_disallowed_file_type(self, app):
        with app.test_request_context():
            fake_pdf = FileStorage(
                stream=io.BytesIO(b"fake pdf content"),
                filename="test_document.pdf",
                content_type="application/pdf",
            )
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="Test Meal",
                calorie_kcal=500,
                protein_g=30,
                carb_g=50,
                fat_g=20,
                description="A test meal.",
                new_photos=[fake_pdf],
            )
            assert form.validate() is False
            assert "new_photos" in form.errors

    def test_accepts_allowed_file_type(self, app):
        with app.test_request_context():
            fake_image = FileStorage(
                stream=io.BytesIO(b"fake image bytes"),
                filename="photo.jpg",
                content_type="image/jpeg",
            )
            form = MealForm(
                logged_date=date.fromisoformat("2024-06-01"),
                name="Test Meal",
                calorie_kcal=500,
                protein_g=30,
                carb_g=50,
                fat_g=20,
                description="A test meal.",
                new_photos=[fake_image],
            )
            assert form.validate() is True


class TestMealQueries:
    def test_get_meals_for_date(self, db, make_user):
        user = make_user()
        meal1 = Meal(
            user_id=user.id,
            name="Breakfast",
            calorie_kcal=300,
            protein_g=20,
            carb_g=40,
            fat_g=10,
            logged_date=date(2024, 6, 1),
        )
        meal2 = Meal(
            user_id=user.id,
            name="Lunch",
            calorie_kcal=600,
            protein_g=30,
            carb_g=70,
            fat_g=20,
            logged_date=date(2024, 6, 1),
        )
        db.session.add_all([meal1, meal2])
        db.session.commit()

        meals = get_meals_for_date(user.id, date(2024, 6, 1))
        assert len(meals) == 2
        assert meals[0].name == "Breakfast"
        assert meals[1].name == "Lunch"

    def test_get_meals_for_date_no_meals(self, db, make_user):
        user = make_user()
        meals = get_meals_for_date(user.id, date(2024, 6, 1))
        assert meals == []


class TestMealRoutes:
    def test_index_route_requires_login(self, client):
        response = client.get("/meals/day/2024-06-01/")
        assert response.status_code == 302

    def test_index_redirects_to_todays_day_view(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )
        response = client.get("/meals/", follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == f"/meals/day/{date.today().isoformat()}/"

    def test_day_view_requires_login(self, client):
        response = client.get(f"/meals/day/{date.today().isoformat()}/")
        assert response.status_code == 302  # Redirect to login

    def test_day_view_displays_meals_and_totals(self, client, make_user, make_meal):
        user = make_user()
        # Log in the user
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        # Create two meals for today
        make_meal(
            user_id=user.id,
            name="Lunch",
            calorie_kcal=600,
            protein_g=30,
            carb_g=70,
            fat_g=20,
            logged_date=date.today(),
        )
        make_meal(
            user_id=user.id,
            name="Dinner",
            calorie_kcal=800,
            protein_g=40,
            carb_g=90,
            fat_g=30,
            logged_date=date.today(),
        )

        assumed_totals = {
            "calories": 1400,
            "proteins": 70,
            "carbs": 160,
            "fats": 50,
        }

        response = client.get(f"/meals/day/{date.today().isoformat()}/")
        assert response.status_code == 200

        # Check that the assumed totals are displayed in the response data
        for key, value in assumed_totals.items():
            assert str(value) in response.get_data(as_text=True)

        # Check that the meal names are displayed in the response data
        assert "Lunch" in response.get_data(as_text=True)
        assert "Dinner" in response.get_data(as_text=True)

    def test_day_view_invalid_date_format(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )
        response = client.get("/meals/day/invalid-date/")
        assert response.status_code == 404
        assert b"Invalid date format" in response.data


class TestAddMealRoute:
    def test_add_meal_requires_login(self, client):
        response = client.get("/meals/add?date_str=2024-06-01")
        assert response.status_code == 302  # Redirect to login

    def test_add_meal_invalid_date(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )
        response = client.get("/meals/add?date_str=invalid-date")
        assert response.status_code == 404
        assert b"Invalid or missing date" in response.data

    def test_add_meal_valid_submission(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            "/meals/add?date_str=2024-06-01",
            data={
                "logged_date": "2024-06-01",
                "name": "Test Meal",
                "calorie_kcal": 500,
                "protein_g": 30,
                "carb_g": 50,
                "fat_g": 20,
                "description": "A test meal.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Test Meal" in response.data

    def test_add_meal_with_photos(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        # Create a fake image file
        fake_image = (io.BytesIO(b"fake image bytes"), "photo.jpg")

        response = client.post(
            "/meals/add?date_str=2024-06-01",
            data={
                "logged_date": "2024-06-01",
                "name": "Test Meal with Photo",
                "calorie_kcal": 600,
                "protein_g": 35,
                "carb_g": 55,
                "fat_g": 25,
                "description": "A test meal with photo.",
                "new_photos": [fake_image],
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Test Meal with Photo" in response.data

    def test_add_meal_invalid_submission(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            "/meals/add?date_str=2024-06-01",
            data={
                "logged_date": "2024-06-01",
                "name": "",  # Missing name
                "calorie_kcal": -100,  # Invalid negative calories
                "protein_g": -10,  # Invalid negative protein
                "carb_g": -20,  # Invalid negative carbs
                "fat_g": -5,  # Invalid negative fats
                "description": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"This field is required" in response.data
            or b"Number must be at least" in response.data
        )


class TestEditMealRoute:
    def test_edit_meal_requires_login(self, client, make_meal, make_user):
        user = make_user()
        meal = make_meal(user_id=user.id)
        response = client.get(f"/meals/edit/{meal.id}")
        assert response.status_code == 302  # Redirect to login

    def test_edit_meal_valid_submission(self, client, make_meal, make_user):
        user = make_user()
        meal = make_meal(user_id=user.id)
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            f"/meals/edit/{meal.id}",
            data={
                "name": "Updated Meal Name",
                "calorie_kcal": 700,
                "protein_g": 40,
                "carb_g": 60,
                "fat_g": 30,
                "description": "Updated description.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Updated Meal Name" in response.data

    def test_edit_meal_invalid_submission(self, client, make_meal, make_user):
        user = make_user()
        meal = make_meal(user_id=user.id)
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            f"/meals/edit/{meal.id}",
            data={
                "name": "",  # Missing name
                "calorie_kcal": -100,  # Invalid negative calories
                "protein_g": -10,  # Invalid negative protein
                "carb_g": -20,  # Invalid negative carbs
                "fat_g": -5,  # Invalid negative fats
                "description": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"This field is required" in response.data
            or b"Number must be at least" in response.data
        )

    def test_edit_another_users_meal(self, client, make_meal, make_user):
        user1 = make_user(username="user1", email="user1@example.com")
        user2 = make_user(username="user2", email="user2@example.com")
        meal = make_meal(user_id=user1.id)
        client.post(
            "/auth/login", data={"email_or_username": user2.username, "password": "password123"}
        )

        response = client.get(f"/meals/edit/{meal.id}")
        assert response.status_code == 404  # User2 should not be able to edit User1's meal


class TestDeleteMealRoute:
    def test_delete_meal_requires_login(self, client, make_meal, make_user):
        user = make_user()
        meal = make_meal(user_id=user.id)
        response = client.post(f"/meals/delete/{meal.id}")
        assert response.status_code == 302  # Redirect to login

    def test_delete_meal_valid(self, client, db, make_meal, make_user):
        user = make_user()
        meal = make_meal(user_id=user.id)
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(f"/meals/delete/{meal.id}", follow_redirects=True)
        assert response.status_code == 200
        assert db.session.get(Meal, meal.id) is None  # Meal should be deleted

    def test_delete_another_users_meal(self, client, make_meal, make_user):
        user1 = make_user(username="user1", email="user1@example.com")
        user2 = make_user(username="user2", email="user2@example.com")
        meal = make_meal(user_id=user1.id)
        client.post(
            "/auth/login", data={"email_or_username": user2.username, "password": "password123"}
        )

        response = client.post(f"/meals/delete/{meal.id}", follow_redirects=True)
        assert response.status_code == 404  # User2 should not be able to delete User1's meal


class TestEstimateWithAIRoute:
    def test_estimate_with_ai_requires_login(self, client):
        response = client.post("/meals/estimate_with_ai", data={"description": "Test meal"})
        assert response.status_code == 302  # Redirect to login

    def test_estimate_with_ai_valid_submission(self, client, make_user, monkeypatch):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        # Mock the estimate_meal function to return a predictable result
        def mock_estimate_meal(description, image_bytes_list=None, client=None):
            return {
                "meal_summary": "Mocked meal summary",
                "calorie_kcal": 500,
                "protein_g": 30,
                "fat_g": 20,
                "carb_g": 50,
                "confidence": "high",
                "assumptions": "Mocked assumptions",
                "source_type": "text_description",
            }

        monkeypatch.setattr("app.meals.routes.estimate_meal", mock_estimate_meal)

        response = client.post(
            "/meals/estimate_with_ai",
            data={"description": "Test meal"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["meal_summary"] == "Mocked meal summary"
        assert json_data["calorie_kcal"] == 500
        assert json_data["protein_g"] == 30
        assert json_data["fat_g"] == 20
        assert json_data["carb_g"] == 50
        assert json_data["confidence"] == "high"
        assert json_data["assumptions"] == "Mocked assumptions"
        assert json_data["source_type"] == "text_description"

    def test_estimate_with_ai_invalid_submission(self, client, make_user):
        user = make_user()
        client.post(
            "/auth/login", data={"email_or_username": user.username, "password": "password123"}
        )

        response = client.post(
            "/meals/estimate_with_ai",
            data={},  # Missing description
            follow_redirects=True,
        )
        assert response.status_code == 400
        json_data = response.get_json()
        # Since description is missing, the AI might return default values or an error message
        assert "error" in json_data


class TestServices:
    def test_compute_totals(self, make_meal):
        user_id = 1
        meal1 = make_meal(user_id=user_id, calorie_kcal=300, protein_g=20, carb_g=40, fat_g=10)
        meal2 = make_meal(user_id=user_id, calorie_kcal=600, protein_g=30, carb_g=70, fat_g=20)

        totals = compute_totals([meal1, meal2])
        assert totals["calories"] == 900
        assert totals["proteins"] == 50
        assert totals["carbs"] == 110
        assert totals["fats"] == 30

    def test_compute_totals_empty_list(self):
        totals = compute_totals([])
        assert totals["calories"] == 0
        assert totals["proteins"] == 0
        assert totals["carbs"] == 0
        assert totals["fats"] == 0


class TestUtils:
    def test_make_unique_filename(self):
        original_filename = "photo.jpg"
        unique_filename = make_unique_filename(original_filename)
        assert unique_filename.endswith(".jpg")
        assert unique_filename != original_filename

    def test_uploaded_files_to_bytes(self, app):
        with app.test_request_context():
            fake_image1 = (io.BytesIO(b"fake image bytes 1"), "photo1.jpg")
            fake_image2 = (io.BytesIO(b"fake image bytes 2"), "photo2.png")

            uploaded_files = [
                FileStorage(
                    stream=fake_image1[0], filename=fake_image1[1], content_type="image/jpeg"
                ),
                FileStorage(
                    stream=fake_image2[0], filename=fake_image2[1], content_type="image/png"
                ),
            ]

            image_bytes_list = uploaded_files_to_bytes(uploaded_files)
            assert len(image_bytes_list) == 2
            assert (
                base64.standard_b64decode(image_bytes_list[0].encode("utf-8"))
                == b"fake image bytes 1"
            )
            assert (
                base64.standard_b64decode(image_bytes_list[1].encode("utf-8"))
                == b"fake image bytes 2"
            )
