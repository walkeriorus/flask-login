import os
class DefaultSettings(object):
    ENV = 'development'
    DEBUG = True
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_PASSWORD = '624531'
    MYSQL_DATABASE_PORT = 3310
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_BD = 'sounds'
    SECRET_KEY = 'bd12c86c6cfe90e3dd8519d38c487097e7cf3b88f321fd78a559212ec8048975'
    CARPETA = os.path.join('tienda/uploads/')
#SECRET_KEY es necesario para poder usar sesiones en Flask.