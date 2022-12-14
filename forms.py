from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class FormularioDeRegistro(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(),Length(max=25)])
    email = StringField('Correo',validators=[DataRequired(),Email()])
    password = PasswordField('Contraseña',validators=[DataRequired(),Length(max=12)])
    submit = SubmitField('Registrarse')