from database.conexion import db

class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    sexo = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(150))

    # NUEVO CAMPO
    riesgo = db.Column(db.String(20), default="No evaluado")

    def __repr__(self):
        return self.nombre