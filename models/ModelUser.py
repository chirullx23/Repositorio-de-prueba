from werkzeug.security import generate_password_hash
from models.entities.User import User

class ModelUser():
    def signin(self, db, usuario):
        try:
            selUsuario = db.connection.cursor()
            selUsuario.execute("SELECT * FROM usuario WHERE correo= %s",(usuario.correo,))
            u = selUsuario.fetchone()
            if u is not None:
                return User(u[0],u[1],u[2],User.validarClave(u[3],usuario.clave),u[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    def signup(self, db, usuario):
        try:
            selUsuario = db.connection.cursor()
            selUsuario.execute("SELECT * FROM usuario WHERE correo= %s",(usuario.correo,))
            existente = selUsuario.fetchone()
            if existente is not None:
                # Ya hay una cuenta registrada con ese correo
                return None

            claveCifrada = generate_password_hash(usuario.clave)
            insUsuario = db.connection.cursor()
            insUsuario.execute(
                "INSERT INTO usuario (nombre, correo, clave, perfil) VALUES (%s, %s, %s, %s)",
                (usuario.nombre, usuario.correo, claveCifrada, "C")
            )
            db.connection.commit()
            nuevoId = insUsuario.lastrowid
            return User(nuevoId, usuario.nombre, usuario.correo, claveCifrada, "C")
        except Exception as ex:
            raise Exception(ex)

    def get_by_id(self, db, id):
        try:
            selUsuario = db.connection.cursor()
            selUsuario.execute("SELECT * FROM usuario WHERE id= %s",(id,))
            u = selUsuario.fetchone()
            if u is not None:
                return User(u[0],u[1],u[2],u[3],u[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
