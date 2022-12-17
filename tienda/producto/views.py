from tienda.producto.models import Product
from dbFunctions import connectDb
from database import db

from flask import render_template
from flask import Blueprint
from flask_login import login_required

product_blueprint = Blueprint('product',__name__)

@product_blueprint.route('/productos',methods=['GET'])
@login_required
def verProductos():
    sql = f"""SELECT * FROM `sounds`.`productos`"""
    
    conn,curr = connectDb(db)
    curr.execute(sql)
            
    productos = list(map(lambda row: Product(row[0],row[1],row[2],row[3]),curr.fetchall()))
    conn.commit()
    
    return render_template('/user/productos.html', products = productos )