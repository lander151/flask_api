from datetime import timedelta
from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt, get_jwt_claims,
)

from models import UserModel, RevokedTokenModel, CitiesModel, Association
from config import TOKEN_EXP_TIME
from run import db
from utils import formatted_results


class UserRegistration(MethodView):
    # TODO: check if user exists

    def post(self):
        user_data = request.json
        username = user_data['username']
        password = UserModel.generate_hash(user_data['password'])
        email = user_data['email']
        new_user = UserModel(
            username=username,
            password=password,
            email=email
        )
        if UserModel.find_by_username(user_data['username']):
            return jsonify({'message': 'User {} already exists'.format(user_data['username'])})

        new_user.save_to_db()

        access_token = create_access_token(identity=user_data['username'])
        refresh_token = create_refresh_token(identity=user_data['username'])

        if new_user:
            return jsonify({
                'result': 'created user %s' % username,
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201, {'ContentType': 'application/json'}
        else:
            return jsonify({'result': 'error creating user'}), 400, {'ContentType': 'application/json'}


class Users(MethodView):

    def get(self):
        result = UserModel.return_all()

        if not result:
            return ({'result': 'NO DATA'}), 404

        return jsonify(result), 200


class UserLogin(MethodView):

    def post(self):
        login_data = request.json

        current_user = UserModel.find_by_username(login_data['username'])
        if not current_user:
            return jsonify({"result': 'User %s doesn't exists" % login_data['username']}), \
                   404, \
                   {'ContentType': 'application/json'}

        if UserModel.verify_hash(login_data['password'], current_user.password):
            payload = {
                'id': current_user.id,
                'username': current_user.username
            }
            access_token = create_access_token(identity=login_data['username'], user_claims=payload,
                                               expires_delta=timedelta(minutes=TOKEN_EXP_TIME))
            refresh_token = create_refresh_token(identity=login_data['username'])

            return jsonify({
                'result': 'Logged in as %s' % login_data['username'],
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201, {'ContentType': 'application/json'}
        else:
            return jsonify({'result': 'error with the login'}), 400, {'ContentType': 'application/json'}


class UserLogoutAccess(MethodView):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return jsonify({'message': 'Access token has been revoked'})
        except:
            return jsonify({'message': 'Something went wrong'}), 500


class UserLogoutRefresh(MethodView):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return jsonify({'message': 'Refresh token has been revoked'})
        except:
            return jsonify({'message': 'Something went wrong'}), 500


class TokenRefresh(MethodView):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify({'access_token': access_token})


class Cities(MethodView):
    @jwt_required
    def get(self):
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        result = CitiesModel().find_by_coords(lat, lon)

        if not result:
            return jsonify({'result': 'NO DATA'}), 404

        return formatted_results(result), 200


class UserCities(MethodView):

    @jwt_required
    def post(self):
            user = get_jwt_claims()

            user_id = user.get('id')
            city_id = request.json.get('city_id')

            a = Association(cities_id=city_id, users_id=user_id)
            db.session.add(a)
            db.session.commit()

            return jsonify({'inserted': 'ok'}), 200, {'ContentType': 'application/json'}

    @jwt_required
    def get(self):
            result_list = list()

            user = get_jwt_claims()
            user_id = user.get('id')

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
            return jsonify(result_list), 200, {'ContentType': 'application/json'}

    @jwt_required
    def delete(self):
        user = get_jwt_claims()
        user_id = user.get('id')

        city_id = request.args.get('city_id')

        asso = Association.query.filter_by(users_id=user_id, cities_id=city_id).first()
        db.session.delete(asso)
        db.session.commit()

        return jsonify({'deleted': 'ok'}), 204, {'ContentType': 'application/json'}