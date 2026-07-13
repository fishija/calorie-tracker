"""Forms for logging and managing user meals and nutritional data."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileSize, MultipleFileField
from wtforms import HiddenField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange


class MealForm(FlaskForm):
    """Form for creating and updating meals with nutritional macros and image uploads.

    Attributes:
        logged_date (HiddenField): The date when the meal was logged, stored as a hidden field.
        name (StringField): The name of the meal.
        calorie_kcal (IntegerField): The caloric content of the meal in kilocalories.
        protein_g (IntegerField): The protein content of the meal in grams.
        carb_g (IntegerField): The carbohydrate content of the meal in grams.
        fat_g (IntegerField): The fat content of the meal in grams.
        description (TextAreaField): A description of the meal.
        new_photos (MultipleFileField): Field for uploading multiple images of the meal.
        submit (SubmitField): A submit button for the form.
    """

    logged_date = HiddenField(validators=[DataRequired()])

    name = StringField("Name", validators=[DataRequired()])
    calorie_kcal = IntegerField(
        "Calories (kcal)", validators=[DataRequired(), NumberRange(min=0, max=10000)]
    )
    protein_g = IntegerField(
        "Proteins (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)]
    )
    carb_g = IntegerField(
        "Carbohydrates (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)]
    )
    fat_g = IntegerField("Fats (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])

    description = TextAreaField("Description")
    new_photos = MultipleFileField(
        "Meal Photos",
        validators=[
            FileSize(max_size=5 * 1024 * 1024, message="Each file must be less than 5MB."),
            FileAllowed(["jpg", "jpeg", "png"], "Images only"),
        ],
    )

    submit = SubmitField("Add Meal")
