from flask import Flask, jsonify
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


@jwt.expired_token_loader
def my_expired_token_callback(self, expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


import models
from endpoints import (
    UserRegistration, UserCities, UserLogin,
    UserLogoutAccess, UserLogoutRefresh, TokenRefresh, Cities
)

app.add_url_rule('/register', view_func=UserRegistration.as_view('register'))
app.add_url_rule('/login', view_func=UserLogin.as_view('login'))
app.add_url_rule('/logout/access', view_func=UserLogoutAccess.as_view('logout_access'))
app.add_url_rule('/logout/refresh', view_func=UserLogoutRefresh.as_view('logout_refresh'))
app.add_url_rule('/token/refresh', view_func=TokenRefresh.as_view('token_refresh'))
app.add_url_rule('/cities', view_func=Cities.as_view('cities'))
app.add_url_rule('/userCity', view_func=UserCities.as_view('user_city'))

# api.add_resource(endpoints.UserRegistration, '/register')
# api.add_resource(endpoints.UserLogin, '/login')
# api.add_resource(endpoints.UserLogoutAccess, '/logout/access')
# api.add_resource(endpoints.UserLogoutRefresh, '/logout/refresh')
# api.add_resource(endpoints.TokenRefresh, '/token/refresh')
# api.add_resource(endpoints.Cities, '/cities')
# api.add_resource(endpoints.UserCities, '/userCity')


def create_app():
    return app
# if __name__ == '__main__':
#     app.run(debug=True)
