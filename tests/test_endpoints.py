from flask import Flask

from run import db, create_app
from flask_testing import TestCase


class EndpointsTestCase(TestCase):

    def __init__(self):


        POSTGRES = {
            'user': 'angular',
            'pw': 'angular',
            'db': 'test_angular_app',
            'host': 'localhost',
            'port': '5432',
        }
        self.POSTGRES_CONFIG_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

        self.TESTING = True

    def create_app(self):
        # pass in test configuration
        return create_app()

    def setUp(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = self.POSTGRES_CONFIG_URI
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()