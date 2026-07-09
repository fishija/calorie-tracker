"""Goal forms."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class GoalForm(FlaskForm):
    """Form for setting nutritional goals.

    Attributes:
        calorie_kcal (IntegerField): Daily calorie goal in kilocalories.
        protein_g (IntegerField): Daily protein goal in grams.
        carb_g (IntegerField): Daily carbohydrate goal in grams.
        fat_g (IntegerField): Daily fat goal in grams.
        submit (SubmitField): Submit button for the form.
    """
    calorie_kcal = IntegerField("Calories (kcal)", validators=[DataRequired(), NumberRange(min=0, max=10000)])
    protein_g = IntegerField("Proteins (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    carb_g = IntegerField("Carbohydrates (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    fat_g = IntegerField("Fats (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    submit = SubmitField("Save Goal")
