"""Tests for auth module."""

from app.auth.forms import LoginForm, RegisterForm
from app.models import User


class TestRegisterForm:
    def test_accepts_valid_data(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "password123",
                    "confirm": "password123",
                }
            )
            assert form.validate() is True

    def test_rejects_mismatched_passwords(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "password123",
                    "confirm": "somethingelse",
                }
            )
            assert form.validate() is False
            assert "confirm" in form.errors

    def test_rejects_missing_email(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "",
                    "username": "newuser",
                    "password": "password123",
                    "confirm": "password123",
                }
            )
            assert form.validate() is False
            assert "email" in form.errors

    def test_rejects_invalid_email(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "not-an-email",
                    "username": "newuser",
                    "password": "password123",
                    "confirm": "password123",
                }
            )
            assert form.validate() is False
            assert "email" in form.errors

    def test_rejects_short_username(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "new@example.com",
                    "username": "ab",  # min length is 3, see forms.py
                    "password": "password123",
                    "confirm": "password123",
                }
            )
            assert form.validate() is False
            assert "username" in form.errors

    def test_rejects_short_password(self, app):
        with app.test_request_context():
            form = RegisterForm(
                data={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "short",  # min length is 8, see forms.py
                    "confirm": "short",
                }
            )
            assert form.validate() is False
            assert "password" in form.errors


class TestLoginForm:
    def test_accepts_valid_data(self, app):
        with app.test_request_context():
            form = LoginForm(
                data={
                    "email_or_username": "someone",
                    "password": "password123",
                }
            )
            assert form.validate() is True

    def test_rejects_missing_password(self, app):
        with app.test_request_context():
            form = LoginForm(
                data={
                    "email_or_username": "someone",
                    "password": "",
                }
            )
            assert form.validate() is False
            assert "password" in form.errors

    def test_rejects_missing_identifier(self, app):
        with app.test_request_context():
            form = LoginForm(
                data={
                    "email_or_username": "",
                    "password": "password123",
                }
            )
            assert form.validate() is False
            assert "email_or_username" in form.errors


class TestRegister:
    def test_get_register_page_returns_200(self, client):
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_valid_registration_creates_a_user(self, client):
        response = client.post(
            "/auth/register",
            data={
                "email": "alice@example.com",
                "username": "alice",
                "password": "password123",
                "confirm": "password123",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        user = User.query.filter_by(email="alice@example.com").first()
        assert user is not None
        assert user.username == "alice"

    def test_valid_registration_logs_the_user_in(self, client):
        client.post(
            "/auth/register",
            data={
                "email": "alice@example.com",
                "username": "alice",
                "password": "password123",
                "confirm": "password123",
            },
        )
        with client.session_transaction() as session:
            assert "_user_id" in session

    def test_duplicate_email_is_rejected(self, client, make_user):
        make_user(email="taken@example.com", username="original")

        response = client.post(
            "/auth/register",
            data={
                "email": "taken@example.com",
                "username": "different",
                "password": "password123",
                "confirm": "password123",
            },
            follow_redirects=True,
        )
        assert b"already exists" in response.data
        # Still only one user with that email in the database.
        assert User.query.filter_by(email="taken@example.com").count() == 1

    def test_password_mismatch_does_not_create_user(self, client):
        response = client.post(
            "/auth/register",
            data={
                "email": "bob@example.com",
                "username": "bob",
                "password": "password123",
                "confirm": "doesnotmatch",
            },
        )
        assert response.status_code == 200
        assert User.query.filter_by(email="bob@example.com").first() is None


class TestLogin:
    def test_login_with_username_and_correct_password(self, client, make_user):
        make_user(email="carol@example.com", username="carol", password="mypassword")

        response = client.post(
            "/auth/login",
            data={"email_or_username": "carol", "password": "mypassword"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        with client.session_transaction() as session:
            assert "_user_id" in session

    def test_login_with_email_instead_of_username(self, client, make_user):
        make_user(email="dave@example.com", username="dave", password="mypassword")

        client.post(
            "/auth/login",
            data={"email_or_username": "dave@example.com", "password": "mypassword"},
        )
        with client.session_transaction() as session:
            assert "_user_id" in session

    def test_login_with_wrong_password_is_rejected(self, client, make_user):
        make_user(email="erin@example.com", username="erin", password="rightpassword")

        response = client.post(
            "/auth/login",
            data={"email_or_username": "erin", "password": "wrongpassword"},
            follow_redirects=True,
        )
        assert b"Invalid credentials" in response.data
        with client.session_transaction() as session:
            assert "_user_id" not in session

    def test_login_with_unknown_identifier_is_rejected(self, client):
        response = client.post(
            "/auth/login",
            data={"email_or_username": "ghost", "password": "whatever"},
            follow_redirects=True,
        )
        assert b"Invalid credentials" in response.data

    def test_already_logged_in_user_is_redirected_away(self, client, make_user):
        make_user(email="gina@example.com", username="gina", password="password123")
        client.post(
            "/auth/login",
            data={"email_or_username": "gina", "password": "password123"},
        )

        response = client.get("/auth/login", follow_redirects=False)
        assert response.status_code == 302  # redirect, not the login page


class TestLogout:
    def test_logout_requires_login(self, client):
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302

    def test_logout_clears_the_session(self, client, make_user):
        make_user(email="frank@example.com", username="frank", password="password123")
        client.post(
            "/auth/login",
            data={"email_or_username": "frank", "password": "password123"},
        )

        response = client.get("/auth/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"logged out" in response.data.lower()

        with client.session_transaction() as session:
            assert "_user_id" not in session
