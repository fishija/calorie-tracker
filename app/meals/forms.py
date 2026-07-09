"""Forms for logging and managing user meals and nutritional data."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class MealForm(FlaskForm):
    """Form for creating and updating meals with nutritional macros and image uploads.

    Attributes:
        name (StringField): The name of the meal.
        calorie_kcal (IntegerField): The caloric content of the meal in kilocalories.
        protein_g (IntegerField): The protein content of the meal in grams.
        carb_g (IntegerField): The carbohydrate content of the meal in grams.
        fat_g (IntegerField): The fat content of the meal in grams.
        description (TextAreaField): A description of the meal.
        new_photos (MultipleFileField): Field for uploading multiple images of the meal.
        submit (SubmitField): A submit button for the form.
    """

    name = StringField("Name", validators=[DataRequired()])
    calorie_kcal = IntegerField("Calories (kcal)", validators=[DataRequired()])
    protein_g = IntegerField("Proteins (g)", validators=[DataRequired()])
    carb_g = IntegerField("Carbohydrates (g)", validators=[DataRequired()])
    fat_g = IntegerField("Fats (g)", validators=[DataRequired()])

    description = TextAreaField("Description")
    new_photos = MultipleFileField(
        "Meal Photos", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only")]
    )

    submit = SubmitField("Add Meal")
