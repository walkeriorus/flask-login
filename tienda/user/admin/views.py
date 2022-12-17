from flask import Blueprint
from flask import render_template,redirect,url_for,flash,current_app
from flask_login import current_user, login_required

from tienda.user.models import User
from tienda.producto.models import Product
from tienda.forms import FormularioCrearProducto,FormularioEditarProducto

from pymysql import Error
from datetime import datetime

from dbFunctions import connectDb,searchUserById
from database import db

from os import path,remove


admin_blueprint = Blueprint('admin',__name__)




@admin_blueprint.route('/error')
@login_required
def usuarioNoAutorizado():
    return render_template('error.html')

@admin_blueprint.route('/productosAdmin')
@login_required
def manipularProductos():
    if current_user.is_admin:
        sql = f"""SELECT * FROM `sounds`.`productos`"""
    
        conn,curr = connectDb(db)
        
        curr.execute(sql)
                
        productos = list(map(lambda row: Product(row[0],row[1],row[2],row[3]),curr.fetchall()))
        
        conn.commit()
        return render_template('admin/productosAdmin.html', products = productos)
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))



@admin_blueprint.route('/crearProducto',methods=['GET','POST'])
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
                _prodImg.save(path.join(current_app.config['CARPETA'], nuevoNombreFoto ))

            
            sql = f"""INSERT INTO `sounds`.`productos`(`nombre`,`precio`,`imagen`)
                    VALUES ('{_prodName}',{_prodPrice},'{nuevoNombreFoto}')"""
            
            conn,curr = connectDb(db)
            
            try:
                curr.execute(sql)
            except Error as e:
                print(e)
                flash('Producto duplicado, producto no añadido.')
                return redirect(url_for('admin.crearProducto'))
            else:
                conn.commit()
                flash('Producto agregado con éxito.')
                return redirect(url_for('admin.crearProducto'))
        else:
            return render_template('admin/cargar-producto.html',form = form)
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/eliminar/<int:product_id>')
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
        remove(path.join(current_app.config['CARPETA'], imagen))

        curr.execute(sql_delete)
        conn.commit()
        flash('Producto eliminado.')
        return redirect(url_for('manipularProductos'))
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@admin_blueprint.route('/edit/<int:product_id>')
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
        return render_template('admin/edit.html',product = producto, form = form)
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/guardar',methods=['POST'])
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
                productImg.save(path.join(current_app.config['CARPETA'], nuevoNombreFoto))
                sql_update = f"""UPDATE `sounds`.`productos`
            SET nombre = '{productName}', precio = {productPrice},imagen='{nuevoNombreFoto}' WHERE id_producto = {productId}"""
                try:
                    remove(path.join(current_app.config['CARPETA'], oldProductImg))
                except  FileNotFoundError:
                    #Si no encuentro el archivo a borrar no hago nada
                    print("\n"*10,"ARCHIVO NO ENCONTRADO"*5,"\n"*10)
                    pass
            else:
                sql_update = f"""UPDATE `sounds`.`productos` SET nombre = '{productName}', precio = {productPrice},imagen='{oldProductImg}' WHERE id_producto = {productId}"""
                
            conn,curr = connectDb(db)
            curr.execute(sql_update)
            conn.commit()
            
            return redirect(url_for('admin.manipularProductos'))
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/usuarios')
@login_required
def mostrarUsuarios():
    if current_user.is_admin:
        sql = "SELECT `user_id`, `user_name`, `user_pass`,`user_role` FROM `sounds`.`usuarios`"
        conn,curr = connectDb(db)
        curr.execute(sql)
        usuarios = curr.fetchall()
        conn.commit()
        return render_template('admin/usuarios.html', usuarios = usuarios)
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/eliminarUsuario/<int:user_id>')
@login_required
def eliminarUsuario(user_id):
    if current_user.is_admin:
        sql_delete = f"""DELETE FROM `sounds`.`usuarios` WHERE user_id = {user_id}"""

        conn,curr = connectDb(db)

        curr.execute(sql_delete)
        conn.commit()
        flash('Usuario eliminado')
        return redirect(url_for('admin.mostrarUsuarios'))
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/verInfo/user/<int:user_id>')
@login_required
def verInformacionDeUsuario( user_id ):
    if current_user.is_admin:
        busqueda = searchUserById(db,'sounds','usuarios','user_id',user_id)
        usuario = busqueda[:3]+busqueda[-1:]
        del busqueda
        return render_template('user-info.html',usuario = usuario)
    else:
        return redirect(url_for('usuarioNoAutorizado'))

@admin_blueprint.route('/makeAdmin/<int:user_id>')
@login_required
def makeAdmin(user_id):
    if current_user.is_admin:
        sql_update = f"""UPDATE `sounds`.`usuarios`
        SET `user_role` = 1 WHERE user_id = {user_id}"""
        conn, curr = connectDb(db)
        curr.execute(sql_update)
        conn.commit()
        return redirect(url_for('admin.mostrarUsuarios'))
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))

@admin_blueprint.route('/makeUser/<int:user_id>')
@login_required
def revokePermissions(user_id):
    if current_user.is_admin:
        sql_update = f"""UPDATE `sounds`.`usuarios`
        SET `user_role` = 0 WHERE user_id = {user_id}"""
        conn, curr = connectDb(db)
        curr.execute(sql_update)
        conn.commit()
        return redirect(url_for('admin.mostrarUsuarios'))
    else:
        return redirect(url_for('admin.usuarioNoAutorizado'))