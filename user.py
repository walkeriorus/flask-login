from werkzeug.security import generate_password_hash,check_password_hash
#generate_password_hash genera una version 'encriptada' del string que recibe como argumento
#Mi forma de explicarlo es, recibe un string y devuelve otro string generado aleatoriamente
#en este caso se esta usando para reforzar la seguridad, para no guardar la contraseña del usuario
#como un string plano que seria legible por cualquiera si accede a la base de datos.
from flask_login import UserMixin
#Esta clase de flask-login tiene todos los atributos que necesita una clase User que funcione con flask-login
#Flask-Login exige que la clase User tenga los siguientes atributos:
#is_authenticated,is_active,is_anonymous,get_id (Para mas informacion ver la documentacion oficial)


class User(UserMixin):
    def __init__(self, id, name, email, password="123456" ):
        self.id = id
        self.name = name
        self.email = email
        self.password = generate_password_hash( password )
        
    def set_password(self, password ):
        self.password = generate_password_hash( password )
        
    @classmethod   
    def check_password(self, hashed_password, password):
        return check_password_hash( hashed_password, password )
    #Este metodo especial se llama cuando la clase no tiene definido un metodo __str__
    #No entiendo en este momento para que sirve
    def __repr__(self):
        return '<User {}>'.format(self.email)
    
    @classmethod
    def get(self, db, id ):
        conn = db.connect()
        curr = conn.cursor()
        
        sql = f"SELECT user_id, user_name, user_email FROM `sounds`.`usuarios` WHERE user_id = '{id}'"
        
        curr.execute(sql)
        
        user = curr.fetchone()
        
        if user != None:
            #Entonces el usuario estaba en la base de datos
            #Como esto se utiliza cuando el usuario ya inicio sesion la contraseña ya no es importante
            return User(user[0],user[1],user[2])
        else:
            return None