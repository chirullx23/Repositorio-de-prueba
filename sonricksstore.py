import os
import traceback
import flask
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
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

    try:
        ModelUser().eliminar(db, id_usuario)
    except Exception:
        db.connection.rollback()
        flask.flash("No se puede eliminar: ese usuario tiene pedidos o productos a su nombre.", "error")
        return flask.redirect(flask.url_for("admin_users"))
    flask.flash("Usuario eliminado.", "exito")
    return flask.redirect(flask.url_for("admin_users"))


# =========================================================
#  CARRITO DE COMPRAS
#  - Mientras el usuario compra, el carrito vive en la sesión
#    (session["carrito"] = {"idbalon": cantidad}).
#  - Al pagar se guarda en la BD: un registro en `pedido`, otro en
#    `realiza` (quién lo hizo) y una fila por balón en `contiene`
#    (idpedido, idbalon, cantidad, precio_unitario). Los precios SIEMPRE se leen de la tabla balon.
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

        cur.execute("INSERT INTO pedido (total) VALUES (%s)", (total,))
        idpedido = cur.lastrowid
        # tu tabla `realiza` une al usuario con su pedido
        cur.execute("INSERT INTO realiza (idusuario, idpedido) VALUES (%s, %s)",
                    (current_user.id, idpedido))

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
    cur.execute("SELECT p.idpedido, p.fecha, p.total, p.estado FROM pedido p "
                "JOIN realiza r ON r.idpedido = p.idpedido "
                "WHERE r.idusuario = %s ORDER BY p.idpedido DESC", (current_user.id,))
    cabeceras = cur.fetchall()

    pedidos = []
    for idpedido, fecha, total, estado in cabeceras:
        cur.execute(
            "SELECT c.idcontiene, c.idbalon, b.nombre, b.imagen, c.cantidad, c.precio_unitario "
            "FROM contiene c JOIN balon b ON b.balon = c.idbalon "
            "WHERE c.idpedido = %s ORDER BY c.idcontiene", (idpedido,))
        lineas = [dict(zip(("idcontiene", "idbalon", "nombre", "imagen",
                            "cantidad", "precio_unitario"), f))
                  for f in cur.fetchall()]
        pedidos.append(dict(idpedido=idpedido, fecha=fecha, total=total, estado=estado, lineas=lineas))
    cur.close()
    return flask.render_template("mis_pedidos.html", pedidos=pedidos)


# =========================================================
#  ADMIN: MANTENIMIENTO DE PRODUCTOS, RUBROS Y PEDIDOS
#  (tablas balon, rubro y pedido/contiene)
# =========================================================

EXT_IMAGEN     = (".jpg", ".jpeg", ".png", ".webp")
ESTADOS_PEDIDO = ("Pendiente", "Enviado", "Entregado", "Cancelado")


def _imagen_existe(nombre):
    """True si el archivo de la foto está de verdad en static/img/."""
    if not nombre:
        return False
    return os.path.isfile(os.path.join(sonricksstoreApp.static_folder, "img", nombre))


sonricksstoreApp.jinja_env.globals["imagen_existe"] = _imagen_existe


def _fecha_texto(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if hasattr(valor, "strftime") else str(valor or "")


def _lista_rubros():
    cur = db.connection.cursor()
    cur.execute("SELECT idrubro, nombre FROM rubro ORDER BY nombre")
    filas = cur.fetchall()
    cur.close()
    return filas


def _guardar_imagen(archivo):
    """Guarda la foto subida en static/img/ sin pisar otra con el mismo nombre.
    Regresa el nombre final o None si no se subió nada."""
    if not archivo or not archivo.filename:
        return None
    base, ext = os.path.splitext(secure_filename(archivo.filename))
    ext = ext.lower()
    if ext not in EXT_IMAGEN:
        raise ValueError("La imagen debe ser .jpg, .jpeg, .png o .webp.")
    base    = (base or "balon")[:30]
    carpeta = os.path.join(sonricksstoreApp.static_folder, "img")
    nombre, n = base + ext, 1
    while os.path.exists(os.path.join(carpeta, nombre)):
        nombre = f"{base}_{n}{ext}"
        n += 1
    archivo.save(os.path.join(carpeta, nombre))
    return nombre


def _leer_producto():
    """Valida el formulario de producto. Lanza ValueError con el mensaje a mostrar."""
    f = flask.request.form
    nombre    = f.get("nombre", "").strip()
    marca     = f.get("marca", "").strip()
    categoria = f.get("categoria", "").strip()
    try:
        precio      = float(f.get("precio", "").replace(",", "."))
        existencias = int(f.get("existencias", ""))
    except ValueError:
        raise ValueError("Precio y existencias deben ser números (existencias, entero).")

    if not nombre or not marca:
        raise ValueError("Nombre y marca son obligatorios.")
    if len(nombre) > 150 or len(marca) > 50:
        raise ValueError("Nombre (máx. 150) o marca (máx. 50) demasiado largos.")
    if precio < 0 or existencias < 0:
        raise ValueError("Precio y existencias no pueden ser negativos.")
    if categoria not in [r[1] for r in _lista_rubros()]:
        raise ValueError("Elige un rubro de la lista (puedes crearlos en Rubros).")

    imagen = _guardar_imagen(flask.request.files.get("archivo")) or f.get("imagen", "").strip()
    if len(imagen) > 50:
        raise ValueError("El nombre de la imagen no puede pasar de 50 caracteres.")
    return dict(nombre=nombre, marca=marca, categoria=categoria,
                precio=precio, existencias=existencias, imagen=imagen)


def _registrar_administra(cur, idusuario, idbalon):
    """Tu tabla `administra`: deja constancia de qué administrador maneja cada producto."""
    cur.execute("SELECT 1 FROM administra WHERE idusuario = %s AND idbalon = %s",
                (idusuario, idbalon))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO administra (idusuario, idbalon) VALUES (%s, %s)",
                    (idusuario, idbalon))


# ---------- PRODUCTOS ----------

@sonricksstoreApp.route("/admin/productos")
@login_required
@admin_requerido
def admin_productos():
    q = flask.request.args.get("q", "").strip()
    cur = db.connection.cursor()
    sql = "SELECT balon, nombre, marca, categoria, precio, existencias, imagen FROM balon"
    params = ()
    if q:
        sql += " WHERE nombre LIKE %s OR marca LIKE %s OR categoria LIKE %s"
        params = (f"%{q}%",) * 3
    cur.execute(sql + " ORDER BY balon DESC", params)
    columnas = [c[0] for c in cur.description]
    productos = [dict(zip(columnas, f)) for f in cur.fetchall()]
    cur.close()
    return flask.render_template("admin_productos.html", productos=productos, q=q)


@sonricksstoreApp.route("/admin/productos/nuevo", methods=["GET", "POST"])
@login_required
@admin_requerido
def admin_producto_nuevo():
    if flask.request.method == "POST":
        try:
            d = _leer_producto()
        except ValueError as e:
            flask.flash(str(e), "error")
            return flask.render_template("admin_producto_form.html", nuevo=True,
                                         producto=flask.request.form, rubros=_lista_rubros())
        cur = db.connection.cursor()
        cur.execute(
            "INSERT INTO balon (nombre, marca, categoria, precio, existencias, imagen) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (d["nombre"], d["marca"], d["categoria"], d["precio"], d["existencias"], d["imagen"]))
        _registrar_administra(cur, current_user.id, cur.lastrowid)
        db.connection.commit()
        cur.close()
        flask.flash("Producto agregado.", "exito")
        return flask.redirect(flask.url_for("admin_productos"))
    return flask.render_template("admin_producto_form.html", nuevo=True,
                                 producto={}, rubros=_lista_rubros())


@sonricksstoreApp.route("/admin/productos/<int:idbalon>/editar", methods=["GET", "POST"])
@login_required
@admin_requerido
def admin_producto_editar(idbalon):
    cur = db.connection.cursor()
    cur.execute("SELECT balon, nombre, marca, categoria, precio, existencias, imagen "
                "FROM balon WHERE balon = %s", (idbalon,))
    fila = cur.fetchone()
    columnas = [c[0] for c in cur.description]
    cur.close()
    if fila is None:
        flask.flash("Ese producto no existe.", "error")
        return flask.redirect(flask.url_for("admin_productos"))
    actual = dict(zip(columnas, fila))

    if flask.request.method == "POST":
        try:
            d = _leer_producto()
        except ValueError as e:
            flask.flash(str(e), "error")
            return flask.render_template("admin_producto_form.html", nuevo=False,
                                         producto={**flask.request.form.to_dict(), "balon": idbalon},
                                         rubros=_lista_rubros())
        cur = db.connection.cursor()
        cur.execute(
            "UPDATE balon SET nombre=%s, marca=%s, categoria=%s, precio=%s, "
            "existencias=%s, imagen=%s WHERE balon=%s",
            (d["nombre"], d["marca"], d["categoria"], d["precio"],
             d["existencias"], d["imagen"], idbalon))
        _registrar_administra(cur, current_user.id, idbalon)
        db.connection.commit()
        cur.close()
        flask.flash("Producto actualizado.", "exito")
        return flask.redirect(flask.url_for("admin_productos"))

    return flask.render_template("admin_producto_form.html", nuevo=False,
                                 producto=actual, rubros=_lista_rubros())


@sonricksstoreApp.route("/admin/productos/<int:idbalon>/eliminar", methods=["POST"])
@login_required
@admin_requerido
def admin_producto_eliminar(idbalon):
    cur = db.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM contiene WHERE idbalon = %s", (idbalon,))
    vendidos = cur.fetchone()[0]
    if vendidos:
        flask.flash("No se puede eliminar: ese producto ya aparece en pedidos. "
                    "Ponle existencias 0 para que salga como Agotado.", "error")
    else:
        cur.execute("DELETE FROM administra WHERE idbalon = %s", (idbalon,))
        cur.execute("DELETE FROM balon WHERE balon = %s", (idbalon,))
        db.connection.commit()
        flask.flash("Producto eliminado.", "exito")
    cur.close()
    return flask.redirect(flask.url_for("admin_productos"))


# ---------- RUBROS ----------

@sonricksstoreApp.route("/admin/rubros")
@login_required
@admin_requerido
def admin_rubros():
    cur = db.connection.cursor()
    cur.execute(
        "SELECT r.idrubro, r.nombre, COUNT(b.balon) FROM rubro r "
        "LEFT JOIN balon b ON b.categoria = r.nombre "
        "GROUP BY r.idrubro, r.nombre ORDER BY r.nombre")
    rubros = [dict(idrubro=a, nombre=b, productos=c) for a, b, c in cur.fetchall()]
    cur.close()
    return flask.render_template("admin_rubros.html", rubros=rubros)


@sonricksstoreApp.route("/admin/rubros/nuevo", methods=["POST"])
@login_required
@admin_requerido
def admin_rubro_nuevo():
    nombre = flask.request.form.get("nombre", "").strip()
    if not nombre or len(nombre) > 60:
        flask.flash("Escribe un nombre de rubro (máximo 60 caracteres).", "error")
        return flask.redirect(flask.url_for("admin_rubros"))
    cur = db.connection.cursor()
    try:
        cur.execute("INSERT INTO rubro (nombre) VALUES (%s)", (nombre,))
        db.connection.commit()
        flask.flash("Rubro agregado.", "exito")
    except Exception:
        db.connection.rollback()
        flask.flash("Ese rubro ya existe.", "error")
    finally:
        cur.close()
    return flask.redirect(flask.url_for("admin_rubros"))


@sonricksstoreApp.route("/admin/rubros/<int:idrubro>/editar", methods=["POST"])
@login_required
@admin_requerido
def admin_rubro_editar(idrubro):
    nuevo = flask.request.form.get("nombre", "").strip()
    if not nuevo or len(nuevo) > 60:
        flask.flash("Escribe un nombre de rubro (máximo 60 caracteres).", "error")
        return flask.redirect(flask.url_for("admin_rubros"))
    cur = db.connection.cursor()
    try:
        cur.execute("SELECT nombre FROM rubro WHERE idrubro = %s", (idrubro,))
        fila = cur.fetchone()
        if fila is None:
            flask.flash("Ese rubro no existe.", "error")
        else:
            # al renombrar, los productos de ese rubro se actualizan también
            cur.execute("UPDATE rubro SET nombre = %s WHERE idrubro = %s", (nuevo, idrubro))
            cur.execute("UPDATE balon SET categoria = %s WHERE categoria = %s", (nuevo, fila[0]))
            db.connection.commit()
            flask.flash("Rubro actualizado.", "exito")
    except Exception:
        db.connection.rollback()
        flask.flash("Ya existe un rubro con ese nombre.", "error")
    finally:
        cur.close()
    return flask.redirect(flask.url_for("admin_rubros"))


@sonricksstoreApp.route("/admin/rubros/<int:idrubro>/eliminar", methods=["POST"])
@login_required
@admin_requerido
def admin_rubro_eliminar(idrubro):
    cur = db.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM balon b JOIN rubro r ON b.categoria = r.nombre "
                "WHERE r.idrubro = %s", (idrubro,))
    if cur.fetchone()[0]:
        flask.flash("No se puede eliminar: todavía hay productos en ese rubro.", "error")
    else:
        cur.execute("DELETE FROM rubro WHERE idrubro = %s", (idrubro,))
        db.connection.commit()
        flask.flash("Rubro eliminado.", "exito")
    cur.close()
    return flask.redirect(flask.url_for("admin_rubros"))


# ---------- PEDIDOS ----------

def _sin_cliente(idu):
    return "Sin cliente asignado" if idu is None else f"Usuario eliminado (#{idu})"


def _clientes():
    """{idusuario: (id, nombre, correo, ...)} usando ModelUser.get_all"""
    return {u[0]: u for u in ModelUser().get_all(db)}


@sonricksstoreApp.route("/admin/pedidos")
@login_required
@admin_requerido
def admin_pedidos():
    estado = flask.request.args.get("estado", "")
    cur = db.connection.cursor()
    sql = ("SELECT p.idpedido, r.idusuario, p.fecha, p.total, p.estado, "
           "COALESCE(SUM(c.cantidad), 0) FROM pedido p "
           "LEFT JOIN realiza r ON r.idpedido = p.idpedido "
           "LEFT JOIN contiene c ON c.idpedido = p.idpedido ")
    params = ()
    if estado in ESTADOS_PEDIDO:
        sql += "WHERE p.estado = %s "
        params = (estado,)
    sql += "GROUP BY p.idpedido, r.idusuario, p.fecha, p.total, p.estado ORDER BY p.idpedido DESC"
    cur.execute(sql, params)
    filas = cur.fetchall()
    cur.close()

    clientes = _clientes()
    pedidos = []
    for idp, idu, fecha, total, est, piezas in filas:
        u = clientes.get(idu)
        pedidos.append(dict(idpedido=idp, idusuario=idu, fecha=_fecha_texto(fecha),
                            total=total, estado=est, piezas=int(piezas),
                            cliente=u[1] if u else _sin_cliente(idu),
                            correo=u[2] if u else ""))
    return flask.render_template("admin_pedidos.html", pedidos=pedidos,
                                 estados=ESTADOS_PEDIDO, filtro=estado)


@sonricksstoreApp.route("/admin/pedidos/<int:idpedido>")
@login_required
@admin_requerido
def admin_pedido_detalle(idpedido):
    cur = db.connection.cursor()
    cur.execute("SELECT p.idpedido, r.idusuario, p.fecha, p.total, p.estado FROM pedido p "
                "LEFT JOIN realiza r ON r.idpedido = p.idpedido WHERE p.idpedido = %s", (idpedido,))
    fila = cur.fetchone()
    if fila is None:
        cur.close()
        flask.flash("Ese pedido no existe.", "error")
        return flask.redirect(flask.url_for("admin_pedidos"))
    cur.execute(
        "SELECT c.idcontiene, c.idbalon, b.nombre, b.imagen, c.cantidad, c.precio_unitario "
        "FROM contiene c LEFT JOIN balon b ON b.balon = c.idbalon "
        "WHERE c.idpedido = %s ORDER BY c.idcontiene", (idpedido,))
    lineas = [dict(zip(("idcontiene", "idbalon", "nombre", "imagen",
                        "cantidad", "precio_unitario"), f)) for f in cur.fetchall()]
    cur.close()

    u = _clientes().get(fila[1])
    pedido = dict(idpedido=fila[0], idusuario=fila[1], fecha=_fecha_texto(fila[2]),
                  total=fila[3], estado=fila[4],
                  cliente=u[1] if u else _sin_cliente(fila[1]),
                  correo=u[2] if u else "")
    return flask.render_template("admin_pedido_detalle.html", pedido=pedido,
                                 lineas=lineas, estados=ESTADOS_PEDIDO)


@sonricksstoreApp.route("/admin/pedidos/<int:idpedido>/estado", methods=["POST"])
@login_required
@admin_requerido
def admin_pedido_estado(idpedido):
    estado = flask.request.form.get("estado", "")
    if estado not in ESTADOS_PEDIDO:
        flask.flash("Estado no válido.", "error")
    else:
        cur = db.connection.cursor()
        cur.execute("UPDATE pedido SET estado = %s WHERE idpedido = %s", (estado, idpedido))
        db.connection.commit()
        cur.close()
        flask.flash(f"Pedido #{idpedido}: {estado}.", "exito")
    volver = flask.request.form.get("volver", "")
    if not volver.startswith("/admin/"):
        volver = flask.url_for("admin_pedidos")
    return flask.redirect(volver)


@sonricksstoreApp.route("/admin/pedidos/<int:idpedido>/eliminar", methods=["POST"])
@login_required
@admin_requerido
def admin_pedido_eliminar(idpedido):
    cur = db.connection.cursor()
    cur.execute("DELETE FROM contiene WHERE idpedido = %s", (idpedido,))
    cur.execute("DELETE FROM realiza WHERE idpedido = %s", (idpedido,))
    cur.execute("DELETE FROM pedido WHERE idpedido = %s", (idpedido,))
    db.connection.commit()
    cur.close()
    flask.flash(f"Pedido #{idpedido} eliminado.", "exito")
    return flask.redirect(flask.url_for("admin_pedidos"))


# =========================================================
#  RUTAS TEMPORALES (los navbars enlazan aquí; se reemplazan
#  cuando construyamos cada página)
# =========================================================

@sonricksstoreApp.route("/rubro/<int:id_rubro>")
def productos_por_rubro(id_rubro):
    flask.flash("Las categorías todavía están en construcción.", "exito")
    return flask.redirect(flask.url_for("home") + "#productos")


# =========================================================
#  ARRANQUE (siempre al final del archivo)
# =========================================================

if __name__ == "__main__":
    sonricksstoreApp.run(debug=True, port=3550)
