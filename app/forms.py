from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField  # Import FileField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed  # Import FileAllowed

# LoginForm class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


# UploadForm class
class UploadForm(FlaskForm):
    file = FileField('Upload Image', validators=[
        InputRequired(),  # Ensure the field is not empty
        FileAllowed(['jpg', 'png'], 'Images only!')  # Only allow .jpg and .png files
    ])
