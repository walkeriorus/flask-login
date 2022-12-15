from flask import Flask, redirect,render_template,request,url_for, flash, send_from_directory
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from user import User
from modelos import Product

from pymysql import Error
from datetime import datetime,date
from os import path,remove
from dbFunctions import connectDb, searchById,searchUserById

from forms import FormularioDeRegistro,FormularioCrearProducto,FormularioEditarProducto


app = Flask(__name__)


db = MySQL()
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def inicio():
    return redirect(url_for('login'))
    
@app.route('/cargarImagen/<imagen>')
@login_required
def cargarImagen(imagen):
    return send_from_directory(app.config['CARPETA'], imagen)    
    
@app.route('/create', methods=['GET','POST'])
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
            return redirect(url_for('inicio'))
        finally:
            conn.commit()
    return render_template('registro.html', form = form )
        
        
        
        
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
                    return redirect(url_for('verProductos'))
                else:
                    return redirect(url_for('manipularProductos'))
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

@app.route('/productos',methods=['GET'])
@login_required
def verProductos():
    sql = f"""SELECT * FROM `sounds`.`productos`"""
    
    conn,curr = connectDb(db)
    curr.execute(sql)
            
    productos = list(map(lambda row: Product(row[0],row[1],row[2],row[3]),curr.fetchall()))
    conn.commit()
    
    return render_template('productos.html', products = productos )

@app.route('/carrito/<int:user_id>/<int:id_prod>')
@login_required
def agregarAlCarrito(user_id,id_prod):
    conn,curr = connectDb(db)
    
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
    
    conn,curr = connectDb(db)
    
    curr.execute(sql_delete)
    conn.commit()
    
    flash(f'Producto quitado del carrito.')
    
    return redirect(url_for('verCarrito',user_id = user_id))


@app.route('/verCarrito/<int:user_id>')
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
    
    total = sum(list(map(lambda producto: producto.price, productos)))
    
    return render_template('carrito.html', products = productos, total = total)


@app.route('/comprarCarrito/<int:user_id>')
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

@app.route('/verCompras/<int:user_id>')
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
    return render_template('compras.html', compras = compras )


#-----------SECCION ADMIN -------------------#
@app.route('/error')
@login_required
def usuarioNoAutorizado():
    return render_template('error.html')

@app.route('/productosAdmin')
@login_required
def manipularProductos():
    if current_user.is_admin:
        sql = f"""SELECT * FROM `sounds`.`productos`"""
    
        conn,curr = connectDb(db)
        
        curr.execute(sql)
                
        productos = list(map(lambda row: Product(row[0],row[1],row[2],row[3]),curr.fetchall()))
        
        conn.commit()
        return render_template('productosAdmin.html', products = productos)
    else:
        return redirect(url_for('usuarioNoAutorizado'))



@app.route('/crearProducto',methods=['GET','POST'])
@login_required
def crearProducto():
    if current_user.is_admin:
        form = FormularioCrearProducto()
        if form.validate_on_submit():
            _prodName = form.name.data
            _prodPrice = form.price.data
            _prodImg = form.image.data
            # Guardamos en now los datos de fecha y hora
            now = datetime.now()

            # Y en tiempo almacenamos una cadena con esos datos
            tiempo = now.strftime("%Y%H%M%S")

            #Si el nombre de la foto ha sido proporcionado en el form...
            if _prodImg.filename!='':
                #...le cambiamos el nombre.
                nuevoNombreFoto=tiempo+_prodImg.filename
                # Guardamos la foto en la carpeta uploads.
                _prodImg.save("uploads/"+nuevoNombreFoto)

            
            sql = f"""INSERT INTO `sounds`.`productos`(`nombre`,`precio`,`imagen`)
                    VALUES ('{_prodName}',{_prodPrice},'{nuevoNombreFoto}')"""
            
            conn,curr = connectDb(db)
            
            try:
                curr.execute(sql)
            except Error as e:
                print(e)
                flash('Producto duplicado, producto no añadido.')
                return redirect(url_for('crearProducto'))
            else:
                conn.commit()
                flash('Producto agregado con éxito.')
                return redirect(url_for('crearProducto'))
        else:
            return render_template('cargar-producto.html',form = form)
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/eliminar/<int:product_id>')
@login_required
def eliminarProducto(product_id):
    if current_user.is_admin:
        sql_select = f"""SELECT imagen FROM `sounds`.`productos`
        WHERE id_producto = {product_id}"""
        sql_delete = f"""DELETE FROM `sounds`.`productos`
        WHERE `id_producto` = {product_id}"""
        conn,curr = connectDb(db)
        curr.execute(sql_select)
        imagen = curr.fetchone()[0]
        remove(path.join(app.config['CARPETA'], imagen))

        curr.execute(sql_delete)
        conn.commit()
        flash('Producto eliminado.')
        return redirect(url_for('manipularProductos'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/edit/<int:product_id>')
@login_required
def editarProducto(product_id):
    if current_user.is_admin:
        form = FormularioEditarProducto()
        sql_select = f"""SELECT * FROM `sounds`.`productos`
        WHERE `id_producto` = {product_id}"""
        
        conn,curr = connectDb(db)
        
        curr.execute(sql_select)
        productInfo = curr.fetchone()
        conn.commit()
        
        producto = Product(productInfo[0],productInfo[1],productInfo[2],productInfo[3])
        return render_template('edit.html',product = producto, form = form)
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/guardar',methods=['POST'])
@login_required
def guardarCambios():
    if current_user.is_admin:
        form = FormularioEditarProducto()
        if form.validate_on_submit():
            productId = form.id.data
            productName = form.name.data
            productPrice = form.price.data
            productImg = form.image.data
            oldProductImg = form.oldImage.data
            # Guardamos en now los datos de fecha y hora
            now = datetime.now()
            print("\n"*10)
            print(f"""
                  { productId}
                  {productName}
                  {productPrice}
                  {productImg}
                  {oldProductImg}""")
            # Y en tiempo almacenamos una cadena con esos datos
            tiempo = now.strftime("%Y%H%M%S")

            #Si el nombre de la foto ha sido proporcionado en el form...
            if productImg.filename!='':
                #...le cambiamos el nombre.
                nuevoNombreFoto=tiempo+productImg.filename
                # Guardamos la foto en la carpeta uploads.
                productImg.save("uploads/"+nuevoNombreFoto)
                sql_update = f"""UPDATE `sounds`.`productos`
            SET nombre = '{productName}', precio = {productPrice},imagen='{nuevoNombreFoto}' WHERE id_producto = {productId}"""
                try:
                    remove(path.join(app.config['CARPETA'], oldProductImg))
                except  FileNotFoundError:
                    #Si no encuentro el archivo a borrar no hago nada
                    print("\n"*10,"ARCHIVO NO ENCONTRADO"*5,"\n"*10)
                    pass
            else:
                sql_update = f"""UPDATE `sounds`.`productos` SET nombre = '{productName}', precio = {productPrice},imagen='{oldProductImg}' WHERE id_producto = {productId}"""
                
            conn,curr = connectDb(db)
            curr.execute(sql_update)
            conn.commit()
            
            return redirect(url_for('manipularProductos'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/usuarios')
@login_required
def mostrarUsuarios():
    if current_user.is_admin:
        sql = "SELECT `user_id`, `user_name`, `user_pass`,`user_role` FROM `sounds`.`usuarios`"
        conn,curr = connectDb(db)
        curr.execute(sql)
        usuarios = curr.fetchall()
        conn.commit()
        return render_template('usuarios.html', usuarios = usuarios)
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/eliminarUsuario/<int:user_id>')
@login_required
def eliminarUsuario(user_id):
    if current_user.is_admin:
        sql_delete = f"""DELETE FROM `sounds`.`usuarios` WHERE user_id = {user_id}"""

        conn,curr = connectDb(db)

        curr.execute(sql_delete)
        conn.commit()
        flash('Usuario eliminado')
        return redirect(url_for('mostrarUsuarios'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/verInfo/user/<int:user_id>')
@login_required
def verInformacionDeUsuario( user_id ):
    if current_user.is_admin:
        busqueda = searchUserById(db,'sounds','usuarios','user_id',user_id)
        usuario = busqueda[:3]+busqueda[-1:]
        del busqueda
        return render_template('user-info.html',usuario = usuario)
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/makeAdmin/<int:user_id>')
@login_required
def makeAdmin(user_id):
    if current_user.is_admin:
        sql_update = f"""UPDATE `sounds`.`usuarios`
        SET `user_role` = 1 WHERE user_id = {user_id}"""
        conn, curr = connectDb(db)
        curr.execute(sql_update)
        conn.commit()
        return redirect(url_for('mostrarUsuarios'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@app.route('/makeUser/<int:user_id>')
@login_required
def revokePermissions(user_id):
    if current_user.is_admin:
        sql_update = f"""UPDATE `sounds`.`usuarios`
        SET `user_role` = 0 WHERE user_id = {user_id}"""
        conn, curr = connectDb(db)
        curr.execute(sql_update)
        conn.commit()
        return redirect(url_for('mostrarUsuarios'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))



if __name__=="__main__":
    app.config.from_object('config.DefaultSettings')
    app.run()