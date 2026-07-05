from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class GoalForm(FlaskForm):
    calorie_kcal = IntegerField("Calories (kcal)", validators=[DataRequired(), NumberRange(min=0, max=10000)])
    protein_g = IntegerField("Proteins (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    carb_g = IntegerField("Carbohydrates (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    fat_g = IntegerField("Fats (g)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    submit = SubmitField("Save Goal")
