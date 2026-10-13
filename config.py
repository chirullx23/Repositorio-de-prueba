class Config:
    SECRET_KEY = 'IEWIWEUWEIEWRUWERIWEURPWEORUWEROPU'
    DEBUG      = True

class DevelopemeetConfig(Config):
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'mysql'
    MYSQL_DB       = 'sonricksstore'


config = {
    'development': DevelopemeetConfig
}
