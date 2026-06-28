from database.conexion import db

class Historial(db.Model):
    __tablename__ = 'historiales'

    id = db.Column(db.Integer, primary_key=True)
    paciente = db.Column(db.String(100))
    fecha = db.Column(db.String(20))
    diagnostico = db.Column(db.String(300))
    tratamiento = db.Column(db.String(300))
    observaciones = db.Column(db.String(500))