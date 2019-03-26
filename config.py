TOKEN_EXP_TIME = 90
POSTGRES = {
    'user': 'angular',
    'pw': 'angular',
    'db': 'angular_app',
    'host': 'localhost',
    'port': '5432',
}
POSTGRES_CONFIG = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

TOKEN_EXP_TIME = 90

SECRET_KEY = 'some-secret-string'
JWT_SECRET_KEY = 'jwt-secret-string'
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
