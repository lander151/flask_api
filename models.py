from sqlalchemy import func, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from run import db
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256
from geoalchemy2 import Geometry

Base = declarative_base()


class CitiesModel(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(255), nullable=False)
    county = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    geom = db.Column(Geometry(geometry_type='multipolygon', srid=4326), nullable=False)

    def find_by_coords(self, lat, lon):
        point = 'POINT(%s %s)' % (lon, lat)
        return CitiesModel.query.filter(
            func.ST_Intersects(func.Geometry(CitiesModel.geom),
                               func.Geometry(func.ST_GeographyFromText(point)))).first()


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'username': x.username,
                'created_at': x.created_at,
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class Association(db.Model):
    __tablename__ = 'UserCities'
    cities_id = db.Column(Integer, ForeignKey('cities.id'), primary_key=True)
    users_id = db.Column(Integer, ForeignKey('users.id'), primary_key=True)


class RevokedTokenModel(db.Model):
        __tablename__ = 'revoked_tokens'
        id = db.Column(db.Integer, primary_key=True)
        jti = db.Column(db.String(120))

        def add(self):
            db.session.add(self)
            db.session.commit()

        @classmethod
        def is_jti_blacklisted(cls, jti):
            query = cls.query.filter_by(jti=jti).first()
            return bool(query)