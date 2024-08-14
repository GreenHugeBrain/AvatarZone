from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired

class RegistrationForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired()])
    email = StringField('ელ. ფოსტა:', validators=[DataRequired()])
    password = PasswordField('პაროლი:', validators=[DataRequired()])
    groupID = SelectField('ვადა', choices=[(5, "5 დღე"), (14, "2 კვირა"), (30, "1 თვე")], validators=[InputRequired()])
    submit = SubmitField('რეგისტრაცია')

class LoginForm(FlaskForm):
    username = StringField('სახელი', validators=[DataRequired()])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    submit = SubmitField('ავტორიზაცია')
