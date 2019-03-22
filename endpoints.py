from flask import jsonify, request
from flask_restful import Resource, reqparse

from run import db
from utils import formatted_results

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from models import UserModel, RevokedTokenModel, CitiesModel, Association

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)
parser.add_argument('email', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    # TODO check if user exists

    def post(self):
        user_data = parser.parse_args()
        username = user_data['username']
        password = UserModel.generate_hash(user_data['password'])
        email = user_data['email']
        new_user = UserModel(
            username=username,
            password=password,
            email=email
        )
        if UserModel.find_by_username(user_data['username']):
            return {'message': 'User {} already exists'.format(user_data['username'])}

        new_user.save_to_db()

        access_token = create_access_token(identity=user_data['username'])
        refresh_token = create_refresh_token(identity=user_data['username'])

        if new_user:
            return {
                'result': 'created user %s' % username,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201, {'ContentType': 'application/json'}
        else:
            return ({'result': 'error creating user'}), 400, {'ContentType': 'application/json'}


class UserLogin(Resource):
    def post(self):

        login_data = parser.parse_args()

        current_user = UserModel.find_by_username(login_data['username'])

        if not current_user:
            return ({"result': 'User %s doesn't exists" % login_data['username']}), \
                   404, \
                   {'ContentType': 'application/json'}

        if UserModel.verify_hash(login_data['password'], current_user.password):

            access_token = create_access_token(identity=login_data['username'])
            refresh_token = create_refresh_token(identity=login_data['username'])

            return ({
                'result': 'Logged in as %s' % login_data['username'],
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201, {'ContentType': 'application/json'}
        else:
            return ({'result': 'error with the login'}), 400, {'ContentType': 'application/json'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class Cities(Resource):

    # @jwt_required
    def get(self):
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        result = CitiesModel().find_by_coords(lat, lon)

        if not result:
            return ({'result': 'NO DATA'}), 404

        return formatted_results(result), 200


class UserCities(Resource):

    def post(self):
            user_id = request.json.get('user_id')
            city_id = request.json.get('city_id')

            a = Association(cities_id=city_id, users_id=user_id)
            db.session.add(a)
            db.session.commit()

            return ({'inserted': 'ok'}), 200, {'ContentType': 'application/json'}

    def get(self):
            result_list = list()
            user_id = request.args.get('user_id')

            results = Association.query.join(CitiesModel, Association.cities_id == CitiesModel.id).add_columns(
                CitiesModel.id,
                CitiesModel.country,
                CitiesModel.region,
                CitiesModel.province,
                CitiesModel.county,
                CitiesModel.city,
                CitiesModel.geom
            ).filter(Association.users_id == user_id)

            if not results:
                return jsonify({'result': 'NO DATA'}), 404, {'ContentType': 'application/json'}

            for result in results:
                result_list.append(formatted_results(result))
            return result_list, 200, {'ContentType': 'application/json'}

    def delete(self):
            user_id = request.args.get('user_id')
            city_id = request.args.get('city_id')

            asso = Association.query.filter_by(users_id=user_id, cities_id=city_id).first()
            db.session.delete(asso)
            db.session.commit()

            return {'deleted': 'ok'}, 204, {'ContentType': 'application/json'}