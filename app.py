from flask import Flask, redirect,render_template,request,url_for, flash
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_required, login_user, logout_user
from user import User

app = Flask(__name__)
app.config.from_object('config.DefaultSettings')


db = MySQL()
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/usuarios')
def mostrarUsuarios():
    sql = "SELECT `user_id`, `user_name`, `user_pass` FROM `sounds`.`usuarios`"
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    conn.commit()
    return render_template('usuarios.html', usuarios = usuarios)
    
    
    
@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    else:
        userName = request.form.get('userName')
        userEmail = request.form.get('userEmail')
        userPass = request.form.get('userPass')
        
        usuario = User( None, userName, userEmail, userPass )
    
        sql = f"""INSERT INTO `sounds`.`usuarios`(`user_name`,`user_email`,`user_pass`)
        VALUES('{usuario.name}','{usuario.email}','{usuario.password}')"""
        
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
    
        return redirect('/')

@app.route('/orders/<int:id>')
@login_required
def showOrders(id):
    
    conn = db.connect()
    curr = conn.cursor()
    
    sql = """SELECT `user_name`,`order_id`, `order_number` 
    FROM `sounds`.`usuarios`,`sounds`.`orders`
    WHERE `usuarios`.`user_id` = %s AND `usuarios`.`user_id`=`orders`.`fk_user_id`"""
    curr.execute(sql, (id) )
    orders = curr.fetchall()
    conn.commit()
    
    return render_template('orders.html', orders = orders)


@login_manager.user_loader
def load_user(user_id):
    return User.get(db,user_id)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    #Si el método no es GET, entonces es POST :-)
    else:
        #Construir un objeto usuario con los datos que llegan del formulario
        _userName = request.form.get('userName')
        _userPass = request.form.get('userPass')
        
        sql = f"""SELECT * FROM `sounds`.`usuarios`
        WHERE `user_name`= '{_userName}'"""
        
        conn = db.connect()
        curr = conn.cursor()
        
        curr.execute(sql)
        dbUserInfo = curr.fetchone()
        if dbUserInfo != None:
            dbUserId,dbUserName, dbUserEmail, dbUserPass = dbUserInfo
            usuario = User(dbUserId,dbUserName,dbUserEmail,_userPass)
        
            #Si el nuevo password hasheado es igual al que estaba en la base de datos entonces el usuario puse bien la contraseña
            logged_in = User.check_password( dbUserPass,_userPass )
            print("logged_in: ", logged_in)
            if logged_in:
                login_user(usuario)
                return redirect(url_for('mostrarUsuarios'))
            else:
                flash('Usuario o contraseña incorrectos')
                return render_template(url_for('inicio'))
        else:
            #el nombre del usuario no existe
            flash('El usuario no existe')
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))


if __name__=="__main__":
    app.run()