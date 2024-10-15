from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired

class HouseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    contact_name = StringField('Contact Name', validators=[DataRequired()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired()])
    image_file = FileField('Main Image')
    additional_images = FileField('Additional Images')
    available = BooleanField('Available')
