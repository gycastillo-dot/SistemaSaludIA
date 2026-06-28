from database.conexion import db

class Cita(db.Model):
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)
    paciente = db.Column(db.String(100))
    fecha = db.Column(db.String(20))
    hora = db.Column(db.String(20))
    motivo = db.Column(db.String(200))
