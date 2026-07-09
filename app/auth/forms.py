"""Authentication forms for user registration and login."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    """Form for new user registration.

    Attributes:
        email (StringField): User's email address.
        username (StringField): Desired username.
        password (PasswordField): Account password.
        confirm (PasswordField): Password confirmation.
        submit (SubmitField): Submit button for the form.
    """
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """Form for user login.

    Allows a user to authenticate using either their email address or
    username, along with their password.

    Attributes:
        email_or_username (StringField): User's email or username.
        password (PasswordField): Account password.
        remember (BooleanField): Option to remember the user.
        submit (SubmitField): Submit button for the form.
    """
    email_or_username = StringField(
        "Email or Username", validators=[DataRequired()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")
