import flask
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from models.entities.User import User
from models.ModelUser import ModelUser

sonricksstoreApp = flask.Flask(__name__)
db               = MySQL(sonricksstoreApp)
adminUsuarios    = LoginManager(sonricksstoreApp)
sonricksstoreApp.config.from_object(config['development'])

@adminUsuarios.user_loader
def agregarUsuario(id):
    return ModelUser().get_by_id(db, id)

@sonricksstoreApp.route("/")
def home():
    return flask.render_template("home.html" )


@sonricksstoreApp.route("/signin", methods=["POST"])
def signin():
    correo = flask.request.form.get("correo", "").strip()
    clave  = flask.request.form.get("clave", "")

    usuario = User(0, "", correo, clave, "")
    usuario_bd = ModelUser().signin(db, usuario)

    # usuario_bd.clave aquí es un booleano: el resultado de comparar
    # la contraseña enviada contra el hash guardado en la base de datos.
    if usuario_bd is not None and usuario_bd.clave:
        login_user(usuario_bd)
        flask.flash("¡Sesión iniciada! Bienvenido de vuelta.", "exito")
        return flask.redirect(flask.url_for("home"))
    else:
        flask.flash("Correo o contraseña incorrectos.", "error")
        return flask.redirect(flask.url_for("home", auth="login"))


@sonricksstoreApp.route("/signup", methods=["POST"])
def signup():
    nombre = flask.request.form.get("nombre", "").strip()
    correo = flask.request.form.get("correo", "").strip()
    clave  = flask.request.form.get("clave", "")

    if not nombre or not correo or not clave:
        flask.flash("Completa todos los campos para crear tu cuenta.", "error")
        return flask.redirect(flask.url_for("home", auth="registro"))

    usuario = User(0, nombre, correo, clave, "")
    resultado = ModelUser().signup(db, usuario)

    if resultado is not None:
        flask.flash("¡Cuenta creada! Ya puedes iniciar sesión.", "exito")
        return flask.redirect(flask.url_for("home", auth="login"))
    else:
        flask.flash("Ese correo ya está registrado. Intenta iniciar sesión.", "error")
        return flask.redirect(flask.url_for("home", auth="registro"))


@sonricksstoreApp.route("/logout")
@login_required
def logout():
    logout_user()
    flask.flash("Sesión cerrada.", "exito")
    return flask.redirect(flask.url_for("home"))


if __name__ == "__main__":
    sonricksstoreApp.run(debug=True, port=3550)
