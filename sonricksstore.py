import flask
from functools import wraps
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
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


@adminUsuarios.unauthorized_handler
def no_autorizado():
    # Si alguien entra a una página privada sin sesión, lo mandamos al
    # inicio con el modal de "Iniciar sesión" abierto.
    flask.flash("Inicia sesión para continuar.", "error")
    return flask.redirect(flask.url_for("home", auth="login"))


def admin_requerido(func):
    """Protege una ruta para que solo usuarios con perfil 'A' (admin) entren."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != "A":
            flask.flash("No tienes permisos de administrador.", "error")
            return flask.redirect(flask.url_for("home"))
        return func(*args, **kwargs)
    return wrapper


# =========================================================
#  TIENDA
# =========================================================

@sonricksstoreApp.route("/")
def home():
    return flask.render_template("home.html")


# =========================================================
#  SESIÓN: iniciar, registrarse, cerrar
# =========================================================

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

    flask.flash("Ese correo ya está registrado. Intenta iniciar sesión.", "error")
    return flask.redirect(flask.url_for("home", auth="registro"))


@sonricksstoreApp.route("/logout")
@login_required
def logout():
    logout_user()
    flask.flash("Sesión cerrada.", "exito")
    return flask.redirect(flask.url_for("home"))


# =========================================================
#  USERS: mi cuenta (todos) + lista de usuarios (solo admin)
# =========================================================

@sonricksstoreApp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if flask.request.method == "POST":
        accion = flask.request.form.get("accion")

        if accion == "datos":
            nombre = flask.request.form.get("nombre", "").strip()
            correo = flask.request.form.get("correo", "").strip()

            if not nombre or not correo:
                flask.flash("Nombre y correo son obligatorios.", "error")
            else:
                try:
                    ModelUser().actualizar_perfil(db, current_user.id, nombre, correo)
                    flask.flash("Datos actualizados.", "exito")
                except Exception:
                    # El correo es UNIQUE en la tabla: si ya existe, MySQL lo rechaza
                    flask.flash("Ese correo ya está en uso por otra cuenta.", "error")

        elif accion == "clave":
            actual = flask.request.form.get("clave_actual", "")
            nueva  = flask.request.form.get("clave_nueva", "")
            usuario_bd = ModelUser().get_by_id(db, current_user.id)

            if usuario_bd is None or not User.validarClave(usuario_bd.clave, actual):
                flask.flash("La contraseña actual no es correcta.", "error")
            elif len(nueva) < 6:
                flask.flash("La contraseña nueva debe tener al menos 6 caracteres.", "error")
            else:
                ModelUser().cambiar_clave(db, current_user.id, nueva)
                flask.flash("Contraseña actualizada.", "exito")

        return flask.redirect(flask.url_for("users"))

    # El administrador ve además la lista de todos los usuarios
    usuarios = []
    if current_user.perfil == "A":
        usuarios = ModelUser().get_all(db)
    return flask.render_template("users.html", usuarios=usuarios)


# =========================================================
#  PANEL DE ADMINISTRADOR
# =========================================================

@sonricksstoreApp.route("/admin")
@login_required
@admin_requerido
def admin_dashboard():
    return flask.render_template("admin_dashboard.html")


@sonricksstoreApp.route("/admin/users")
@login_required
@admin_requerido
def admin_users():
    todos = ModelUser().get_all(db)

    # Resumen sobre todos los usuarios (aunque haya una búsqueda activa)
    total    = len(todos)
    admins   = sum(1 for u in todos if u[4] == "A")
    clientes = total - admins

    # Búsqueda opcional por nombre o correo:  /admin/users?q=ana
    q = flask.request.args.get("q", "").strip()
    usuarios = todos
    if q:
        q_min = q.lower()
        usuarios = [u for u in todos if q_min in u[1].lower() or q_min in u[2].lower()]

    return flask.render_template(
        "admin_users.html",
        usuarios=usuarios, q=q, total=total, admins=admins, clientes=clientes
    )


@sonricksstoreApp.route("/admin/users/<int:id_usuario>/editar", methods=["GET", "POST"])
@login_required
@admin_requerido
def admin_usuario_editar(id_usuario):
    if flask.request.method == "POST":
        nombre = flask.request.form.get("nombre", "").strip()
        correo = flask.request.form.get("correo", "").strip()
        perfil = flask.request.form.get("perfil", "C")
        if perfil not in ("A", "C"):
            perfil = "C"

        if not nombre or not correo:
            flask.flash("Nombre y correo son obligatorios.", "error")
            return flask.redirect(flask.url_for("admin_usuario_editar", id_usuario=id_usuario))

        try:
            ModelUser().actualizar(db, id_usuario, nombre, correo, perfil)
        except Exception:
            flask.flash("Ese correo ya está en uso por otra cuenta.", "error")
            return flask.redirect(flask.url_for("admin_usuario_editar", id_usuario=id_usuario))

        flask.flash("Usuario actualizado.", "exito")
        return flask.redirect(flask.url_for("admin_users"))

    # GET: mostrar el formulario con los datos actuales
    usuario = ModelUser().get_by_id(db, id_usuario)
    if usuario is None:
        flask.flash("Ese usuario no existe.", "error")
        return flask.redirect(flask.url_for("admin_users"))

    # get_by_id regresa un objeto User; la plantilla espera una tupla como
    # la que regresa get_all, así que la armamos aquí
    usuario_tupla = (usuario.id, usuario.nombre, usuario.correo, usuario.clave, usuario.perfil)
    return flask.render_template("admin_usuario_editar.html", usuario=usuario_tupla)


@sonricksstoreApp.route("/admin/users/<int:id_usuario>/eliminar", methods=["POST"])
@login_required
@admin_requerido
def admin_usuario_eliminar(id_usuario):
    # Evita que el admin se elimine a sí mismo sin querer
    if id_usuario == current_user.id:
        flask.flash("No puedes eliminar tu propia cuenta desde aquí.", "error")
        return flask.redirect(flask.url_for("admin_users"))

    ModelUser().eliminar(db, id_usuario)
    flask.flash("Usuario eliminado.", "exito")
    return flask.redirect(flask.url_for("admin_users"))


# =========================================================
#  RUTAS TEMPORALES (los navbars enlazan aquí; se reemplazan
#  cuando construyamos cada página)
# =========================================================

@sonricksstoreApp.route("/mis-pedidos")
@login_required
def mis_pedidos():
    flask.flash("Mis pedidos todavía está en construcción.", "exito")
    return flask.redirect(flask.url_for("home"))


@sonricksstoreApp.route("/rubro/<int:id_rubro>")
def productos_por_rubro(id_rubro):
    flask.flash("Las categorías todavía están en construcción.", "exito")
    return flask.redirect(flask.url_for("home") + "#productos")


@sonricksstoreApp.route("/admin/productos")
@login_required
@admin_requerido
def admin_productos():
    flask.flash("Productos todavía está en construcción.", "exito")
    return flask.redirect(flask.url_for("admin_dashboard"))


@sonricksstoreApp.route("/admin/rubros")
@login_required
@admin_requerido
def admin_rubros():
    flask.flash("Rubros todavía está en construcción.", "exito")
    return flask.redirect(flask.url_for("admin_dashboard"))


@sonricksstoreApp.route("/admin/pedidos")
@login_required
@admin_requerido
def admin_pedidos():
    flask.flash("Pedidos todavía está en construcción.", "exito")
    return flask.redirect(flask.url_for("admin_dashboard"))


# =========================================================
#  ARRANQUE (siempre al final del archivo)
# =========================================================

if __name__ == "__main__":
    sonricksstoreApp.run(debug=True, port=3550)
