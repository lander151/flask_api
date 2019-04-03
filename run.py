from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import POSTGRES_CONFIG_URI, SECRET_KEY, JWT_BLACKLIST_TOKEN_CHECKS, JWT_SECRET_KEY

app = Flask(__name__)
app.config['JWT_SECRETE_KEY'] = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CONFIG_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PROPAGATE_EXCEPTIONS '] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = JWT_BLACKLIST_TOKEN_CHECKS

jwt = JWTManager(app)

db = SQLAlchemy(app)
CORS(app)


@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


import models
from endpoints import (
    UserRegistration, UserCities, UserLogin,
    UserLogoutAccess, UserLogoutRefresh, TokenRefresh, Cities, Users
)

app.add_url_rule('/register', view_func=UserRegistration.as_view('register'))
app.add_url_rule('/login', view_func=UserLogin.as_view('login'))
app.add_url_rule('/logout/access', view_func=UserLogoutAccess.as_view('logout_access'))
app.add_url_rule('/logout/refresh', view_func=UserLogoutRefresh.as_view('logout_refresh'))
app.add_url_rule('/token/refresh', view_func=TokenRefresh.as_view('token_refresh'))
app.add_url_rule('/cities', view_func=Cities.as_view('cities'))
app.add_url_rule('/userCity', view_func=UserCities.as_view('user_city'))
app.add_url_rule('/user', view_func=Users.as_view('users'))


def create_app():
    return app
