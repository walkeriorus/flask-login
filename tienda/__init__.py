from flask import Flask,render_template,send_from_directory
from tienda.producto.views import product_blueprint
from tienda.user.views import user_blueprint
from tienda.user.admin.views import admin_blueprint
from flask_login import login_required
from os import path

app = Flask(__name__)
app.register_blueprint(product_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/cargarImagen/<imagen>')
@login_required
def cargarImagen(imagen):
    return send_from_directory('uploads', imagen)