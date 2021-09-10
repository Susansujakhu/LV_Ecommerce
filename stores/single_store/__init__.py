from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
import logging
import sys

app = Flask(__name__,
	template_folder='templates',
	static_folder='static')

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# app.config.from_pyfile('../config.py')
app.config.from_object("config.DevelopmentConfig")
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.cache = {}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dlrlanipbonlce:9cb49a1064792c62b117eebcc4ef16c6e1023958ad3445a4974f76f552b0ce67@ec2-44-196-170-156.compute-1.amazonaws.com/dcog583f0vde5f'
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
login_manager.login_view = '/account'
login_manager.login_message_category = 'info'


from single_store import routes
