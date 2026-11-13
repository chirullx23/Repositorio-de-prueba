class Config:
    SECRET_KEY = 'IEWIWEUWEIEWRUWERIWEURPWEORUWEROPU'
    DEBUG      = True

class DevelopemeetConfig(Config):
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'mysql'
    MYSQL_DB       = 'sonricksstore'

class Mailconfig(config):  
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'osvaldo.villalobos@alumnos.udg.mx'
    MAIL_PASWORD = 'qbur pvpa egza gltx'
    MAIL_DEFAULT_SENDER = 'osvaldo.villalobos@alumnos.udg.mx'
    MAIL_ASC11_ATTACHIMENTS = True

config = {
    'development': DevelopemeetConfig,
    'mail'       : Mailconfig
}
