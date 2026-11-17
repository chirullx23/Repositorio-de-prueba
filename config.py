import os


class Config:
    SECRET_KEY = 'IEWIWEUWEIEWRUWERIWEURPWEORUWEROPU'
    DEBUG      = True

class DevelopemeetConfig(Config):
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'mysql'
    MYSQL_DB       = 'sonricksstore'

class MailConfig(Config):
    # Pon aquí tu correo de Gmail y tu "contraseña de aplicación" de 16 letras
    # (sin espacios), o defínelos como variables de entorno MAIL_USERNAME y
    # MAIL_PASSWORD. No subas 
    # Si el puerto 587 no conecta (redes de escuela), usa este par en su lugar:
    #   MAIL_PORT = 465 ; MAIL_USE_TLS = False ; MAIL_USE_SSL = Trtu contraseña real a GitHub.
    #ue
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = 'osvaldo.villalobos2229@alumnos.udg.mx'
    MAIL_PASSWORD       = 'IEWIWEUWEIEWRUWERIWEURPWEORUWEROPU'
    MAIL_DEFAULT_SENDER ='osvaldo.villalobos2229@alumnos.udg.mx'
    MAIL_ASCII_ATTACHMENTS = True


config = {
    'development': DevelopemeetConfig,
    'mail':        MailConfig            
}
