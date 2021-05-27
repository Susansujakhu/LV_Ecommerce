
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message

app = Flask(__name__,
	template_folder='templates',
	static_folder='static')
app.config.from_object("config.DevelopmentConfig")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sushansujakhu14@localhost/ecommerce'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# # POSTGRES = {
# #     'user': 'postgres',
# #     'pw': 'sushansujakhu14',
# #     'db': 'flask_test',
# #     'host': 'localhost',
# #     'port': '5432',
# # }
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# # ...app config...
# print(app.config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



from single_store import routes
