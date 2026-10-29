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

def admin_requerido(func):
    """Protege una ruta para que solo usuarios con perfil 'A' (admin) entren."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != "A":
            flash("No tienes permisos de administrador.", "error")
            return redirect(url_for("home"))
        return func(*args, **kwargs)
    return wrapper


@sonricksstoreApp.route("/admin")
@login_required
@admin_requerido
def admin_dashboard():
    return render_template("admin_dashboard.html")


@sonricksstoreApp.route("/admin/usuarios")
@login_required
@admin_requerido
def admin_usuarios():
    usuarios = ModelUser().get_all(db)
    return render_template("admin_usuarios.html", usuarios=usuarios)


@sonricksstoreApp.route("/admin/usuarios/<int:id_usuario>/eliminar", methods=["POST"])
@login_required
@admin_requerido
def admin_usuario_eliminar(id_usuario):
    # Evita que el admin se elimine a sí mismo sin querer
    if id_usuario == current_user.id:
        flash("No puedes eliminar tu propia cuenta desde aquí.", "error")
        return redirect(url_for("admin_usuarios"))

    ModelUser().eliminar(db, id_usuario)
    flash("Usuario eliminado.", "exito")
    return redirect(url_for("admin_usuarios"))


@sonricksstoreApp.route("/admin/usuarios/<int:id_usuario>/editar", methods=["GET", "POST"])
@login_required
@admin_requerido
def admin_usuario_editar(id_usuario):
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        perfil = request.form.get("perfil", "C")

        if not nombre or not correo:
            flash("Nombre y correo son obligatorios.", "error")
            return redirect(url_for("admin_usuario_editar", id_usuario=id_usuario))

        ModelUser().actualizar(db, id_usuario, nombre, correo, perfil)
        flash("Usuario actualizado.", "exito")
        return redirect(url_for("admin_usuarios"))

    # GET: mostrar el formulario con los datos actuales
    usuario = ModelUser().get_by_id(db, id_usuario)
    if usuario is None:
        flash("Ese usuario no existe.", "error")
        return redirect(url_for("admin_usuarios"))

    # get_by_id regresa un objeto User; el template espera una tupla como
    # la que regresa get_all, así que la armamos aquí para reusar el mismo template
    usuario_tupla = (usuario.id, usuario.nombre, usuario.correo, usuario.clave, usuario.perfil)
    return render_template("admin_usuario_editar.html", usuario=usuario_tupla)


