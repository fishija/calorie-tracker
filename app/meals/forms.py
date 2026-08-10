"""Forms for logging and managing user meals and nutritional data."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileSize, MultipleFileField
from wtforms import (
    DateField,
    DecimalField,
    HiddenField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget


class CommaSeparatedListField(StringField):
    """Custom field to handle comma-separated lists of values."""
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            # Split by comma and filter out any empty strings
            self.data = [d.strip() for d in valuelist[0].split(',') if d.strip()]
        else:
            self.data = []


class CopyMealsForm(FlaskForm):
    """Form for copying meals from one date to another."""
    from_date = DateField("Copy from date", validators=[DataRequired()])
    to_dates = CommaSeparatedListField(
        "Copy to dates",
        validators=[DataRequired("Please select at least one date.")]
    )
    meals = SelectMultipleField(
        "Meals to copy",
        coerce=int,
        validators=[DataRequired("Please select at least one meal to copy.")],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )


class MealForm(FlaskForm):
    """Form for creating and updating meals with nutritional macros and image uploads.

    No products are associated with this form, and it is intended for quick meal logging.

    Attributes:
        logged_date (HiddenField): The date when the meal was logged, stored as a hidden field.
        name (StringField): The name of the meal.
        calorie_kcal (DecimalField): The caloric content of the meal in kilocalories.
        protein_g (DecimalField): The protein content of the meal in grams.
        carb_g (DecimalField): The carbohydrate content of the meal in grams.
        fat_g (DecimalField): The fat content of the meal in grams.
        description (TextAreaField): A description of the meal.
        new_photos (MultipleFileField): Field for uploading multiple images of the meal.
        submit (SubmitField): A submit button for the form.
    """

    logged_date = HiddenField(validators=[InputRequired()])

    name = StringField("Name", validators=[DataRequired()])
    calorie_kcal = DecimalField(
        "Calories (kcal)",
        validators=[InputRequired(), NumberRange(min=0, max=10000)],
        places=1,
        render_kw={
            "placeholder": "e.g. 450",
        },
    )
    protein_g = DecimalField(
        "Proteins (g)",
        validators=[InputRequired(), NumberRange(min=0, max=1000)],
        places=1,
        render_kw={
            "placeholder": "e.g. 35",
        },
    )
    carb_g = DecimalField(
        "Carbohydrates (g)",
        validators=[InputRequired(), NumberRange(min=0, max=1000)],
        places=1,
        render_kw={
            "placeholder": "e.g. 40",
        },
    )
    fat_g = DecimalField(
        "Fats (g)",
        validators=[InputRequired(), NumberRange(min=0, max=1000)],
        places=1,
        render_kw={
            "placeholder": "e.g. 15.5",
        },
    )

    description = TextAreaField("Description")
    new_photos = MultipleFileField(
        "Meal Photos",
        validators=[
            FileSize(max_size=5 * 1024 * 1024, message="Each file must be less than 5MB."),
            FileAllowed(["jpg", "jpeg", "png"], "Images only"),
        ],
    )

    submit = SubmitField("Add Meal")
