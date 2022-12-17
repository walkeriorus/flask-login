from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField,HiddenField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError,DataRequired, Email, Length,Regexp,NumberRange

class CustomLength(Length):
    def __call__(self, form, field):
        length = field.data and len(field.data) or 0
        if length >= self.min and (self.max == -1 or length <= self.max):
            return

        if self.message is not None:
            message = self.message

        elif self.max == -1:
            message = field.ngettext(
                "El campo dene tener al menos %(min)d caracter.",
                "El campo dene tener al menos %(min)d caracteres.",
                self.min,
            )
        elif self.min == -1:
            message = field.ngettext(
                "El campo no puede contener mas de %(max)d caracter.",
                "El campo no puede contener mas de %(max)d caracteres.",
                self.max,
            )
        elif self.min == self.max:
            message = field.ngettext(
                "El campo debe contener exactamente %(max)d caracter.",
                "El campo debe contener exactamente %(max)d caracteres.",
                self.max,
            )
        else:
            message = field.gettext(
                "El campo debe contener entre %(min)d y %(max)d caracteres."
            )

        raise ValidationError(message % dict(min=self.min, max=self.max, length=length))

passPattern = '[0-9]{6,12}'
badPassword = 'La contraseña solo puede contener números, debe tener una longitud de al menos 6 digitos.'

class FormularioDeRegistro(FlaskForm):
    name = StringField('Nombre',validators=[DataRequired(message="Debe ingresar un nombre."),CustomLength(min=6,max=25)],description="juan")
    email = StringField('Correo',validators=[DataRequired(),Email()])
    password = PasswordField('Contraseña',validators=[DataRequired(),Length(max=12),Regexp(regex=passPattern, message=badPassword)])
    submit = SubmitField('Registrarse')
    
class FormularioCrearProducto(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    price = FloatField('Precio',validators=[DataRequired(message="El producto debe tener un precio."),NumberRange(min=1,max=10000000)])
    image = FileField('Imagen', validators=[FileRequired(message='Seleccione un archivo.')])
    submit = SubmitField('Crear producto')
    
class FormularioEditarProducto(FlaskForm):
    id = HiddenField()
    name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    price = FloatField('Precio',validators=[DataRequired(message="El producto debe tener un precio."),NumberRange(min=1,max=10000000)])
    image = FileField('Imagen', validators=[FileRequired(message='Seleccione un archivo.')])
    oldImage = HiddenField()
    submit = SubmitField('Guardar cambios')