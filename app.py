from flask import Flask, redirect,render_template,request,url_for, flash
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_required, login_user, logout_user
from user import User
from modelos import Product

from pymysql import Error

app = Flask(__name__)
app.config.from_object('config.DefaultSettings')


db = MySQL()
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def inicio():
    return redirect(url_for('login'))

@app.route('/usuarios')
@login_required
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
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
        except Error as e:
            print(e)
            flash('El nombre de usuario ya existe,intente con otro nombre.')
            return redirect(url_for('create'))
        else:
            conn.commit()
            return redirect(url_for('inicio'))

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
                return redirect(url_for('verProductos'))
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('login'))
        else:
            #el nombre del usuario no existe
            flash('El usuario no existe')
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))

@app.route('/crearProducto',methods=['GET','POST'])
@login_required
def crearProducto():
    if request.method == 'POST':
        _prodName = request.form.get('productName')
        _prodPrice = request.form.get('productPrice')
        
        sql = f"""INSERT INTO `sounds`.`productos`(`nombre`,`precio`)
                VALUES ('{_prodName}',{_prodPrice})"""
        
        conn = db.connect()
        curr = conn.cursor()
        
        try:
            curr.execute(sql)
        except Error as e:
            print(e)
            flash('Ha ocurrido un error, producto no añadido')
            return redirect(url_for('crearProducto'))
        else:
            conn.commit()
            flash('Producto agregado con éxito.')
            return redirect(url_for('crearProducto'))
    else:
        return render_template('cargar-producto.html')

@app.route('/productos',methods=['GET'])
@login_required
def verProductos():
    sql = f"""SELECT * FROM `sounds`.`productos`"""
    
    conn = db.connect()
    curr = conn.cursor()
    
    curr.execute(sql)
            
    productos = list(map(lambda row: Product(row[0],row[1],row[2],row[3]),curr.fetchall()))
    
    return render_template('productos.html', products = productos )

@app.route('/carrito/<int:user_id>/<int:id_prod>')
@login_required
def agregarAlCarrito(user_id,id_prod):
    conn = db.connect()
    curr = conn.cursor()
    
    sql = f"""INSERT INTO `sounds`.`carrito`(fk_user_id,fk_id_producto)
    VALUES({user_id},{id_prod})
    """
    curr.execute(sql)
    conn.commit()
    
    return redirect(url_for('verProductos'))

@app.route('/quitarDelCarrito/<int:user_id>/<int:product_id>')
@login_required
def quitarDelCarrito(user_id,product_id):
    
    sql_delete = f"""DELETE FROM `sounds`.`carrito`
    WHERE `fk_user_id`={user_id} AND `fk_id_producto`={product_id}"""
    
    conn = db.connect()
    curr = conn.cursor()
    
    curr.execute(sql_delete)
    conn.commit()
    
    flash(f'Elimnación de producto éxitosa.')
    
    return redirect(url_for('verCarrito',user_id = user_id))


@app.route('/verCarrito/<int:user_id>')
@login_required
def verCarrito(user_id):
    sql = f"""SELECT `productos`.`id_producto`, `productos`.`nombre`, `productos`.`precio`, `productos`.`imagen` 
    FROM `sounds`.`productos`, `sounds`.`carrito`, `sounds`.`usuarios`
    WHERE `productos`.`id_producto` = `carrito`.`fk_id_producto` AND `carrito`.`fk_user_id` = `usuarios`.`user_id`
    AND `usuarios`.`user_id`={user_id};"""
    conn = db.connect()
    curr = conn.cursor()
    curr.execute(sql)
    productos = list(map(lambda row : Product(row[0],row[1],row[2],row[3]), curr.fetchall()))
    conn.commit()
    return render_template('carrito.html', products = productos)

if __name__=="__main__":
    app.run()