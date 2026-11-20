import os
import traceback
import flask
from urllib.parse import urlparse
from functools import wraps
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models.entities.User import User
from models.ModelUser import ModelUser

sonricksstoreApp = flask.Flask(__name__)
adminUsuarios    = LoginManager(sonricksstoreApp)
sonricksstoreApp.config.from_object(config['development'])
sonricksstoreApp.config.from_object(config['mail'])
db               = MySQL(sonricksstoreApp)
mail             = Mail(sonricksstoreApp)   # va DESPUÉS de cargar la config (lee MAIL_*)


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


def enviar_correo_bienvenida(nombre, correo):
    """Manda el correo de bienvenida. Regresa True si se envió, False si falló.
    Si falla (sin internet, credenciales mal, etc.) el registro NO se cancela;
    el motivo exacto se imprime en la terminal."""
    usuario_smtp = sonricksstoreApp.config.get("MAIL_USERNAME", "")
    clave_smtp   = sonricksstoreApp.config.get("MAIL_PASSWORD", "")
    if usuario_smtp.startswith("TU_") or clave_smtp.startswith("TU_"):
        print("CORREO NO ENVIADO: falta poner tu correo y tu contraseña de "
        "aplicación en config.py (MailConfig).")
        return False

    try:
        msg = Message(subject="Bienvenido a Sonricks Store", recipients=[correo])
        msg.body = (f"Hola {nombre}, tu cuenta en Sonricks Store ya está lista. "
                    "¡Gracias por registrarte!")
        msg.html = flask.render_template("user_mail.html", nombre=nombre)
        mail.send(msg)
        return True
    except Exception as e:
        print("CORREO NO ENVIADO:", type(e).__name__, "-", e)
        traceback.print_exc()
        return False


# =========================================================
#  TIENDA
# =========================================================

@sonricksstoreApp.route("/")
def home():
    # Lee los balones de la tabla `balon` y se queda solo con los que
    # tienen su archivo de imagen dentro de static/img/
    cur = db.connection.cursor()
    cur.execute(
        "SELECT balon, nombre, marca, categoria, precio, existencias, imagen "
        "FROM balon ORDER BY categoria, nombre"
    )
    columnas = [c[0] for c in cur.description]
    filas    = cur.fetchall()
    cur.close()

    balones = []
    for fila in filas:
        b = dict(zip(columnas, fila))
        ruta = os.path.join(sonricksstoreApp.static_folder, "img", b["imagen"])
        if os.path.isfile(ruta):
            balones.append(b)

    return flask.render_template("home.html", balones=balones)


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
        if enviar_correo_bienvenida(nombre, correo):
            flask.flash("¡Cuenta creada! Te enviamos un correo de bienvenida. Ya puedes iniciar sesión.", "exito")
        else:
            flask.flash("¡Cuenta creada! Ya puedes iniciar sesión (no pudimos enviar el correo de bienvenida).", "exito")
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
#  CARRITO DE COMPRAS
#  - Mientras el usuario compra, el carrito vive en la sesión
#    (session["carrito"] = {"idbalon": cantidad}).
#  - Al pagar se guarda en la BD: un registro en `pedido` y una
#    fila por balón en `contiene` (idpedido, idbalon, cantidad,
#    precio_unitario). Los precios SIEMPRE se leen de la tabla balon.
# =========================================================

def leer_carrito():
    """Regresa (items, total, cantidad_total) con datos frescos de la BD."""
    carrito = flask.session.get("carrito", {})
    if not carrito:
        return [], 0.0, 0

    ids = [int(i) for i in carrito]
    marcadores = ",".join(["%s"] * len(ids))
    cur = db.connection.cursor()
    cur.execute(
        "SELECT balon, nombre, marca, precio, existencias, imagen "
        f"FROM balon WHERE balon IN ({marcadores})", ids
    )
    filas = cur.fetchall()
    cur.close()

    items, total, cantidad_total = [], 0.0, 0
    for idbalon, nombre, marca, precio, existencias, imagen in filas:
        cantidad = min(int(carrito.get(str(idbalon), 0)), int(existencias))
        if cantidad <= 0:
            continue
        subtotal = round(float(precio) * cantidad, 2)
        items.append(dict(idbalon=idbalon, nombre=nombre, marca=marca,
                          precio=float(precio), existencias=int(existencias),
                          imagen=imagen, cantidad=cantidad, subtotal=subtotal))
        total += subtotal
        cantidad_total += cantidad
    return items, round(total, 2), cantidad_total


@sonricksstoreApp.context_processor
def datos_carrito():
    """Deja carrito_items / carrito_total / carrito_cantidad disponibles en
    TODAS las plantillas (para el globito del carrito)."""
    try:
        items, total, cantidad = leer_carrito()
    except Exception:
        items, total, cantidad = [], 0.0, 0
    return dict(carrito_items=items, carrito_total=total, carrito_cantidad=cantidad)


def _existencias(idbalon):
    cur = db.connection.cursor()
    cur.execute("SELECT nombre, existencias FROM balon WHERE balon = %s", (idbalon,))
    fila = cur.fetchone()
    cur.close()
    return fila   # (nombre, existencias) o None


def _volver(abrir=False):
    """Regresa a la página de donde vino el usuario (solo dentro de este sitio).
    Si abrir=True, el panel del carrito se abre solo al cargar."""
    destino = flask.url_for("home")
    ref = flask.request.referrer
    if ref:
        u = urlparse(ref)
        if u.netloc == flask.request.host and u.path:
            destino = u.path
    if abrir:
        destino += "?carrito=abierto"
    ancla = flask.request.form.get("ancla", "")
    if ancla.isalnum():
        destino += "#" + ancla
    return flask.redirect(destino)


@sonricksstoreApp.route("/carrito")
def ver_carrito():
    return flask.render_template("carrito.html")


@sonricksstoreApp.route("/carrito/agregar/<int:idbalon>", methods=["POST"])
def carrito_agregar(idbalon):
    fila = _existencias(idbalon)
    if fila is None:
        flask.flash("Ese balón ya no existe.", "error")
        return _volver()

    nombre, existencias = fila
    carrito = dict(flask.session.get("carrito", {}))
    actual = int(carrito.get(str(idbalon), 0))
    if actual >= existencias:
        flask.flash(f"Ya tienes en tu carrito todas las existencias de «{nombre}».", "error")
    else:
        carrito[str(idbalon)] = actual + 1
        flask.session["carrito"] = carrito
    return _volver(abrir=True)


@sonricksstoreApp.route("/carrito/cambiar/<int:idbalon>", methods=["POST"])
def carrito_cambiar(idbalon):
    accion = flask.request.form.get("accion")
    carrito = dict(flask.session.get("carrito", {}))
    clave = str(idbalon)

    if clave in carrito:
        cantidad = int(carrito[clave]) + (1 if accion == "mas" else -1)
        if accion == "mas":
            fila = _existencias(idbalon)
            if fila is None or cantidad > fila[1]:
                flask.flash("No hay más existencias de ese balón.", "error")
                cantidad = int(carrito[clave])
        if cantidad <= 0:
            del carrito[clave]
        else:
            carrito[clave] = cantidad
        flask.session["carrito"] = carrito

    return _volver(abrir=flask.request.form.get("panel") == "1")


@sonricksstoreApp.route("/carrito/quitar/<int:idbalon>", methods=["POST"])
def carrito_quitar(idbalon):
    carrito = dict(flask.session.get("carrito", {}))
    carrito.pop(str(idbalon), None)
    flask.session["carrito"] = carrito
    return _volver(abrir=flask.request.form.get("panel") == "1")


@sonricksstoreApp.route("/carrito/vaciar", methods=["POST"])
def carrito_vaciar():
    flask.session.pop("carrito", None)
    return _volver()


@sonricksstoreApp.route("/carrito/pagar", methods=["POST"])
@login_required
def carrito_pagar():
    items, total, _ = leer_carrito()
    if not items:
        flask.flash("Tu carrito está vacío.", "error")
        return flask.redirect(flask.url_for("home"))

    cur = db.connection.cursor()
    try:
        # Revisa existencias de nuevo (y bloquea las filas) antes de vender
        for it in items:
            cur.execute("SELECT existencias FROM balon WHERE balon = %s FOR UPDATE",
                        (it["idbalon"],))
            existencias = cur.fetchone()[0]
            if existencias < it["cantidad"]:
                raise ValueError(f"Solo quedan {existencias} de «{it['nombre']}».")

        cur.execute("INSERT INTO pedido (idusuario, total) VALUES (%s, %s)",
                    (current_user.id, total))
        idpedido = cur.lastrowid

        for it in items:
            cur.execute(
                "INSERT INTO contiene (idpedido, idbalon, cantidad, precio_unitario) "
                "VALUES (%s, %s, %s, %s)",
                (idpedido, it["idbalon"], it["cantidad"], it["precio"]))
            cur.execute("UPDATE balon SET existencias = existencias - %s WHERE balon = %s",
                        (it["cantidad"], it["idbalon"]))
        db.connection.commit()
    except ValueError as e:
        db.connection.rollback()
        flask.flash(str(e), "error")
        return flask.redirect(flask.url_for("ver_carrito"))
    except Exception as e:
        db.connection.rollback()
        print("ERROR al guardar el pedido:", type(e).__name__, "-", e)
        flask.flash("No se pudo guardar tu pedido. Intenta de nuevo.", "error")
        return flask.redirect(flask.url_for("ver_carrito"))
    finally:
        cur.close()

    flask.session.pop("carrito", None)
    flask.flash(f"¡Pedido #{idpedido} realizado! Gracias por tu compra.", "exito")
    return flask.redirect(flask.url_for("mis_pedidos"))


@sonricksstoreApp.route("/mis-pedidos")
@login_required
def mis_pedidos():
    cur = db.connection.cursor()
    cur.execute("SELECT idpedido, fecha, total FROM pedido "
                "WHERE idusuario = %s ORDER BY idpedido DESC", (current_user.id,))
    cabeceras = cur.fetchall()

    pedidos = []
    for idpedido, fecha, total in cabeceras:
        cur.execute(
            "SELECT c.idcontiene, c.idbalon, b.nombre, b.imagen, c.cantidad, c.precio_unitario "
            "FROM contiene c JOIN balon b ON b.balon = c.idbalon "
            "WHERE c.idpedido = %s ORDER BY c.idcontiene", (idpedido,))
        lineas = [dict(zip(("idcontiene", "idbalon", "nombre", "imagen",
                            "cantidad", "precio_unitario"), f))
                  for f in cur.fetchall()]
        pedidos.append(dict(idpedido=idpedido, fecha=fecha, total=total, lineas=lineas))
    cur.close()
    return flask.render_template("mis_pedidos.html", pedidos=pedidos)


# =========================================================
#  RUTAS TEMPORALES (los navbars enlazan aquí; se reemplazan
#  cuando construyamos cada página)
# =========================================================

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
