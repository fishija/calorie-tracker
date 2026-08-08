"""Goal forms."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, StopValidation


class StrictIntegerField(IntegerField):
    """Custom IntegerField that strictly enforces integer input."""

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(valuelist[0])
            except ValueError:
                self.data = None
                raise ValueError("Decimals are not allowed. Please enter a whole number.")

    def pre_validate(self, form):
        """Stop validation on error.

        Prevents "Decimals are not allowed. Please enter a whole number."
        and "Number must be between 0 and 10000." being displayed at the same time.
        """
        if self.process_errors:
            raise StopValidation()


class GoalForm(FlaskForm):
    """Form for setting nutritional goals.

    Attributes:
        calorie_kcal (StrictIntegerField): Daily calorie goal in kilocalories.
        protein_g (StrictIntegerField): Daily protein goal in grams.
        carb_g (StrictIntegerField): Daily carbohydrate goal in grams.
        fat_g (StrictIntegerField): Daily fat goal in grams.
        submit (SubmitField): Submit button for the form.
    """

    calorie_kcal = StrictIntegerField(
        "Calories (kcal)",
        validators=[InputRequired("This field is required."), NumberRange(min=0, max=10000)],
        render_kw={
            "step": "100",
            "placeholder": "e.g. 2400",
        },
    )
    protein_g = StrictIntegerField(
        "Proteins (g)",
        validators=[InputRequired("This field is required."), NumberRange(min=0, max=1000)],
        render_kw={
            "placeholder": "e.g. 160",
        },
    )
    carb_g = StrictIntegerField(
        "Carbohydrates (g)",
        validators=[InputRequired("This field is required."), NumberRange(min=0, max=1000)],
        render_kw={
            "placeholder": "e.g. 280",
        },
    )
    fat_g = StrictIntegerField(
        "Fats (g)",
        validators=[InputRequired("This field is required."), NumberRange(min=0, max=1000)],
        render_kw={
            "placeholder": "e.g. 70",
        },
    )
    submit = SubmitField("Save Goal")
