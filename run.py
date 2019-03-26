from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import POSTGRES_CONFIG, SECRET_KEY, JWT_BLACKLIST_TOKEN_CHECKS, JWT_SECRET_KEY

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
CORS(app)


@app.before_first_request
def create_tables():
    db.create_all()


app.config['JWT_SECRETE_KEY'] = JWT_SECRET_KEY
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = JWT_BLACKLIST_TOKEN_CHECKS


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


import endpoints, models


api.add_resource(endpoints.UserRegistration, '/register')
api.add_resource(endpoints.UserLogin, '/login')
api.add_resource(endpoints.UserLogoutAccess, '/logout/access')
api.add_resource(endpoints.UserLogoutRefresh, '/logout/refresh')
api.add_resource(endpoints.TokenRefresh, '/token/refresh')
api.add_resource(endpoints.Cities, '/cities')
api.add_resource(endpoints.UserCities, '/userCity')


# if __name__ == '__main__':
#     app.run(debug=True)
