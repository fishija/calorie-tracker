"""Authentication routes for user registration, login, and logout."""

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegisterForm
from app.db import db
from app.models import User

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle new user registration.

    Returns:
        Response: Rendered registration template, or a redirect to
            ``main.index`` / ``auth.register`` depending on outcome.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        username = form.username.data.strip()

        existing = User.query.filter(
            (db.func.lower(User.email) == email) | (db.func.lower(User.username) == username)
        ).first()

        if existing:
            flash("Email or username already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User(email=email, username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login.

    Allows user to login using either their email address or username, along with their password.

    Returns:
        Response: Rendered login template, or a redirect to the ``next``
            page / ``main.index`` / ``auth.login`` depending on outcome.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_username.data.strip().lower()

        user = User.query.filter(
            (db.func.lower(User.email) == identifier) | (db.func.lower(User.username) == identifier)
        ).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid credentials.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember.data)

        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to the login page.

    Returns:
        Response: Redirect to ``auth.login`` with a flashed confirmation
            message.
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
