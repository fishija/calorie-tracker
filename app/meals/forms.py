from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class MealForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    calorie_kcal = IntegerField("Calories (kcal)", validators=[DataRequired()])
    protein_g = IntegerField("Proteins (g)", validators=[DataRequired()])
    carb_g = IntegerField("Carbohydrates (g)", validators=[DataRequired()])
    fat_g = IntegerField("Fats (g)", validators=[DataRequired()])
    
    description = TextAreaField("Description")
    new_photos = MultipleFileField(
        "Meal Photos",
          validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only")]
    )

    submit = SubmitField("Add Meal")
