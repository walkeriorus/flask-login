from tienda.user.models import User
from tienda.producto.models import Product
from tienda.forms import FormularioDeRegistro

from dbFunctions import connectDb
from database import db


from flask import request, render_template,redirect,url_for,flash
from flask import Blueprint
from flask_login import login_required,current_user,login_user,logout_user

from pymysql import Error
from datetime import datetime,date

user_blueprint = Blueprint('user',__name__)

@user_blueprint.route('/create', methods=['GET','POST'])
def create():
    form = FormularioDeRegistro()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        usuario = User(None,name,email,password,0)
        sql_insert = f"""INSERT INTO `sounds`.`usuarios`(`user_name`,`user_email`,`user_pass`,`user_role`)
        VALUES('{usuario.name}','{usuario.email}','{usuario.password}',{usuario.is_admin})"""
        
        conn,curr = connectDb(db)
        try:
            curr.execute(sql_insert)
        except Error as e:
            print("\n"*10,e,"\n"*10)
            flash("El nombre de usuario ya existe")
            return redirect(url_for('create', form = form ) )
        else:
            return redirect(url_for('index'))
        finally:
            conn.commit()
    return render_template('registro.html', form = form )

@user_blueprint.route('/login', methods=['GET','POST'])
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
        
        conn, curr = connectDb(db)
        
        curr.execute(sql)
        dbUserInfo = curr.fetchone()
        conn.commit()
        
        if dbUserInfo != None:
            dbUserId,dbUserName, dbUserEmail, dbUserPass, db_userRole = dbUserInfo
            usuario = User(dbUserId,dbUserName,dbUserEmail,_userPass, db_userRole)
        
            #Si el nuevo password hasheado es igual al que estaba en la base de datos entonces el usuario puse bien la contraseña
            logged_in = User.check_password( dbUserPass,_userPass )
            print("logged_in: ", logged_in)
            if logged_in:
                login_user(usuario)
                if not current_user.is_admin:
                    return redirect(url_for('product.verProductos'))
                else:
                    return redirect(url_for('admin.manipularProductos'))
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('login'))
        else:
            #el nombre del usuario no existe
            flash('El usuario no existe')
            return redirect(url_for('login'))
        
@user_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@user_blueprint.route('/carrito/<int:user_id>/<int:id_prod>')
@login_required
def agregarAlCarrito(user_id,id_prod):
    conn,curr = connectDb(db)
    
    sql = f"""INSERT INTO `sounds`.`carrito`(fk_user_id,fk_id_producto)
    VALUES({user_id},{id_prod})
    """
    curr.execute(sql)
    conn.commit()
    
    return redirect(url_for('product.verProductos'))

@user_blueprint.route('/quitarDelCarrito/<int:user_id>/<int:product_id>')
@login_required
def quitarDelCarrito(user_id,product_id):
    
    sql_delete = f"""DELETE FROM `sounds`.`carrito`
    WHERE `fk_user_id`={user_id} AND `fk_id_producto`={product_id}"""
    
    conn,curr = connectDb(db)
    
    curr.execute(sql_delete)
    conn.commit()
    
    flash(f'Producto quitado del carrito.')
    
    return redirect(url_for('user.verCarrito',user_id = user_id))


@user_blueprint.route('/verCarrito/<int:user_id>')
@login_required
def verCarrito(user_id):
    sql = f"""SELECT `productos`.`id_producto`, `productos`.`nombre`, `productos`.`precio`, `productos`.`imagen` 
    FROM `sounds`.`productos`, `sounds`.`carrito`, `sounds`.`usuarios`
    WHERE `productos`.`id_producto` = `carrito`.`fk_id_producto` AND `carrito`.`fk_user_id` = `usuarios`.`user_id`
    AND `usuarios`.`user_id`={user_id};"""
    conn,curr = connectDb(db)
    curr.execute(sql)
    productos = list(map(lambda row : Product(row[0],row[1],row[2],row[3]), curr.fetchall()))
    conn.commit()
    
    
    return render_template('user/carrito.html', products = productos )

@user_blueprint.context_processor
def total_carrito_processor():
    def total( productos ):
        total_a_pagar = sum(list(map(lambda producto: producto.price, productos)))
        return total_a_pagar
    return { 'total': total }
        


@user_blueprint.route('/comprarCarrito/<int:user_id>')
@login_required
def comprarCarrito( user_id ):
    
    sql_select_carrito = f"""SELECT * FROM `sounds`.`carrito` WHERE fk_user_id = {user_id}"""
    conn , curr = connectDb(db)
    curr.execute(sql_select_carrito)
    carrito = curr.fetchall()
    
    now = datetime.now()
    fecha_actual = date(now.year,now.month,now.day).isoformat()
    print("\n"*10,fecha_actual,"\n"*10)
    
    for fila in carrito:
        curr.execute(f"""INSERT INTO `sounds`.`compras`(fk_user_id, fk_id_producto, fecha)
    VALUES({fila[0]},{fila[1]},'{fecha_actual}')""")
        
    del carrito
    curr.execute(f"""DELETE FROM `sounds`.`carrito` WHERE fk_user_id = {user_id}""")
    conn.commit()
    
    return redirect(url_for('verCarrito', user_id = user_id))

@user_blueprint.route('/verCompras/<int:user_id>')
@login_required
def verCompras(user_id):
    
    sql = f"""SELECT productos.id_producto,productos.nombre,productos.imagen,productos.precio, 
compras.fecha
FROM SOUNDS.compras
INNER JOIN SOUNDS.productos ON compras.fk_id_producto = productos.id_producto
AND compras.fk_user_id = {user_id}"""
    conn, curr = connectDb(db)
    curr.execute(sql)
    compras = curr.fetchall()
    
    
    curr.execute(sql)
    conn.commit()
    return render_template('user/compras.html', compras = compras )

