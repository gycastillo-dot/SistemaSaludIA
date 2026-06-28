import os
from datetime import datetime

import joblib
from flask import Flask, render_template, request, redirect, session, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


from database.conexion import db
from models.paciente import Paciente
from models.cita import Cita
from models.historial import Historial


app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

instance_path = os.path.join(BASE_DIR, 'instance')
os.makedirs(instance_path, exist_ok=True)

reportes_path = os.path.join(BASE_DIR, 'reportes')
os.makedirs(reportes_path, exist_ok=True)

app.config['SECRET_KEY'] = 'saludia2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

modelo_diabetes = joblib.load(
    os.path.join(BASE_DIR, "modelos_entrenados", "diabetes_model.pkl")
)


@app.route('/')
def inicio():
    return render_template("inicio.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        if usuario == 'admin' and password == '1234':
            session['usuario'] = usuario
            return redirect('/dashboard')

        return render_template(
            'login.html',
            error="Usuario o contraseña incorrectos"
        )

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')

    total_pacientes = Paciente.query.count()
    total_citas = Cita.query.count()
    total_historiales = Historial.query.count()
    riesgo_alto = Paciente.query.filter_by(riesgo="Alto").count()

    return render_template(
        'dashboard.html',
        pacientes=total_pacientes,
        citas=total_citas,
        historiales=total_historiales,
        riesgo=riesgo_alto
    )


@app.route('/pacientes')
def pacientes():
    if 'usuario' not in session:
        return redirect('/login')

    lista_pacientes = Paciente.query.all()
    return render_template('pacientes.html', pacientes=lista_pacientes)


@app.route('/agregar_paciente', methods=['GET', 'POST'])
def agregar_paciente():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nuevo = Paciente(
            nombre=request.form['nombre'],
            edad=request.form['edad'],
            sexo=request.form['sexo'],
            telefono=request.form['telefono'],
            direccion=request.form['direccion'],
            riesgo=request.form.get('riesgo', 'No evaluado')
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect('/pacientes')

    return render_template('agregar_paciente.html')


@app.route('/citas')
def citas():
    if 'usuario' not in session:
        return redirect('/login')

    lista_citas = Cita.query.all()
    return render_template('citas.html', citas=lista_citas)


@app.route('/agregar_cita', methods=['GET', 'POST'])
def agregar_cita():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nueva = Cita(
            paciente=request.form['paciente'],
            fecha=request.form['fecha'],
            hora=request.form['hora'],
            motivo=request.form['motivo']
        )

        db.session.add(nueva)
        db.session.commit()

        return redirect('/citas')

    return render_template('agregar_cita.html')


@app.route('/historiales')
def historiales():
    if 'usuario' not in session:
        return redirect('/login')

    lista = Historial.query.all()
    return render_template('historiales.html', historiales=lista)


@app.route('/agregar_historial', methods=['GET', 'POST'])
def agregar_historial():
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nuevo = Historial(
            paciente=request.form['paciente'],
            fecha=request.form['fecha'],
            diagnostico=request.form['diagnostico'],
            tratamiento=request.form['tratamiento'],
            observaciones=request.form['observaciones']
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect('/historiales')

    return render_template('agregar_historial.html')

@app.route('/prediccion', methods=['GET', 'POST'])
def prediccion():
    if 'usuario' not in session:
        return redirect('/login')

    resultado = None
    error = None

    pacientes = Paciente.query.all()

    if request.method == 'POST':
        try:
            id_paciente = int(request.form['paciente_id'])

            edad = int(request.form['edad'])
            glucosa = int(request.form['glucosa'])
            presion = int(request.form['presion'])
            imc = float(request.form['imc'])

            pred = modelo_diabetes.predict([[edad, glucosa, presion, imc]])

            paciente = Paciente.query.get(id_paciente)

            if pred[0] == 1:
                resultado = "⚠️ RIESGO ALTO DE DIABETES"
                paciente.riesgo = "Alto"
            else:
                resultado = "✅ RIESGO BAJO DE DIABETES"
                paciente.riesgo = "Bajo"

            db.session.commit()

        except ValueError:
            error = "Por favor complete todos los campos con números válidos."

        except Exception as e:
            error = "Ocurrió un error al procesar la predicción."

    return render_template(
        'prediccion.html',
        resultado=resultado,
        error=error,
        pacientes=pacientes
    )




@app.route('/reportes')
def reportes():
    if 'usuario' not in session:
        return redirect('/login')

    return render_template('reportes.html')


@app.route('/reporte_pacientes')
def reporte_pacientes():
    if 'usuario' not in session:
        return redirect('/login')

    ruta = os.path.join(reportes_path, 'reporte_pacientes.pdf')

    pdf = canvas.Canvas(ruta, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(170, 750, "REPORTE DE PACIENTES - SALUDIA")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 725, "Fecha: " + datetime.now().strftime("%d/%m/%Y %H:%M"))

    y = 690
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "ID")
    pdf.drawString(90, y, "Nombre")
    pdf.drawString(260, y, "Edad")
    pdf.drawString(320, y, "Sexo")
    pdf.drawString(400, y, "Riesgo")

    y -= 20
    pdf.setFont("Helvetica", 10)

    pacientes = Paciente.query.all()

    for p in pacientes:
        pdf.drawString(50, y, str(p.id))
        pdf.drawString(90, y, str(p.nombre))
        pdf.drawString(260, y, str(p.edad))
        pdf.drawString(320, y, str(p.sexo))
        pdf.drawString(400, y, str(p.riesgo))

        y -= 20

        if y < 60:
            pdf.showPage()
            y = 750

    pdf.save()
    return send_file(ruta, as_attachment=True)


@app.route('/reporte_citas')
def reporte_citas():
    if 'usuario' not in session:
        return redirect('/login')

    ruta = os.path.join(reportes_path, 'reporte_citas.pdf')

    pdf = canvas.Canvas(ruta, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(190, 750, "REPORTE DE CITAS - SALUDIA")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 725, "Fecha: " + datetime.now().strftime("%d/%m/%Y %H:%M"))

    y = 690
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "ID")
    pdf.drawString(90, y, "Paciente")
    pdf.drawString(250, y, "Fecha")
    pdf.drawString(340, y, "Hora")
    pdf.drawString(420, y, "Motivo")

    y -= 20
    pdf.setFont("Helvetica", 10)

    citas = Cita.query.all()

    for c in citas:
        pdf.drawString(50, y, str(c.id))
        pdf.drawString(90, y, str(c.paciente))
        pdf.drawString(250, y, str(c.fecha))
        pdf.drawString(340, y, str(c.hora))
        pdf.drawString(420, y, str(c.motivo))

        y -= 20

        if y < 60:
            pdf.showPage()
            y = 750

    pdf.save()
    return send_file(ruta, as_attachment=True)


@app.route('/reporte_riesgo_alto')
def reporte_riesgo_alto():
    if 'usuario' not in session:
        return redirect('/login')

    ruta = os.path.join(reportes_path, 'reporte_riesgo_alto.pdf')

    pdf = canvas.Canvas(ruta, pagesize=letter)

    # ENCABEZADO
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(110, 770, "CENTRO MÉDICO VIRGEN DEL CARMEN")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(145, 745, "REPORTE DE PACIENTES CON RIESGO ALTO")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        50,
        720,
        "Fecha de emisión: " + datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    # ENCABEZADOS DE LA TABLA
    y = 690

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(50, y, "ID")
    pdf.drawString(90, y, "Nombre")
    pdf.drawString(250, y, "Edad")
    pdf.drawString(310, y, "Sexo")
    pdf.drawString(380, y, "Teléfono")
    pdf.drawString(470, y, "Riesgo")

    y -= 20

    pdf.setFont("Helvetica", 10)

    pacientes = Paciente.query.filter_by(riesgo="Alto").all()

    if len(pacientes) == 0:
        pdf.drawString(50, y, "No existen pacientes clasificados con riesgo alto.")
    else:
        for p in pacientes:

            pdf.drawString(50, y, str(p.id))
            pdf.drawString(90, y, p.nombre)
            pdf.drawString(250, y, str(p.edad))
            pdf.drawString(310, y, p.sexo)
            pdf.drawString(380, y, p.telefono)
            pdf.drawString(470, y, p.riesgo)

            y -= 20

            if y <= 60:

                pdf.showPage()

                pdf.setFont("Helvetica-Bold", 18)
                pdf.drawString(110, 770, "CENTRO MÉDICO VIRGEN DEL CARMEN")

                pdf.setFont("Helvetica-Bold", 14)
                pdf.drawString(145, 745, "REPORTE DE PACIENTES CON RIESGO ALTO")

                pdf.setFont("Helvetica", 10)
                pdf.drawString(
                    50,
                    720,
                    "Fecha de emisión: " + datetime.now().strftime("%d/%m/%Y %H:%M")
                )

                y = 690

                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(50, y, "ID")
                pdf.drawString(90, y, "Nombre")
                pdf.drawString(250, y, "Edad")
                pdf.drawString(310, y, "Sexo")
                pdf.drawString(380, y, "Teléfono")
                pdf.drawString(470, y, "Riesgo")

                y -= 20
                pdf.setFont("Helvetica", 10)

    pdf.save()

    return send_file(
        ruta,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)