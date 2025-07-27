import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('backend/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/alquiler', methods=['POST'])
def crear_alquiler():
    data = request.get_json()

    # Extraer datos del cliente
    nombre = data.get('nombre')
    segundo_nombre = data.get('segundo_nombre')
    apellido = data.get('apellido')
    segundo_apellido = data.get('segundo_apellido')
    cedula = data.get('cedula')
    edad = data.get('edad')
    direccion = data.get('direccion')

    # Extraer datos del alquiler
    modelo_auto = data.get('modelo_auto')
    metodo_pago = data.get('metodo_pago')
    total = data.get('total')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insertar cliente o obtener su id si ya existe
    cursor.execute('SELECT id FROM clientes WHERE cedula = ?', (cedula,))
    cliente = cursor.fetchone()
    if cliente:
        cliente_id = cliente['id']
    else:
        cursor.execute(
            'INSERT INTO clientes (nombre, segundo_nombre, apellido, segundo_apellido, cedula, edad, direccion) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (nombre, segundo_nombre, apellido, segundo_apellido, cedula, edad, direccion)
        )
        cliente_id = cursor.lastrowid

    # Obtener id del auto
    cursor.execute('SELECT id, disponibles FROM autos WHERE modelo = ?', (modelo_auto,))
    auto = cursor.fetchone()
    if not auto:
        conn.close()
        return jsonify({'error': 'Auto no encontrado'}), 404
    if auto['disponibles'] <= 0:
        conn.close()
        return jsonify({'error': 'No hay autos disponibles de este modelo'}), 400

    auto_id = auto['id']

    # Insertar alquiler
    cursor.execute(
        'INSERT INTO alquileres (auto_id, cliente_id, metodo_pago, total) VALUES (?, ?, ?, ?)',
        (auto_id, cliente_id, metodo_pago, total)
    )
    alquiler_id = cursor.lastrowid

    # Actualizar disponibilidad de autos
    cursor.execute('UPDATE autos SET disponibles = disponibles - 1 WHERE id = ?', (auto_id,))

    conn.commit()
    conn.close()

    return jsonify({'alquiler_id': alquiler_id}), 201

def poblar_autos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM autos")
    if cursor.fetchone()[0] == 0:
        autos_iniciales = [
            ('Toyota Corolla', 5),
            ('Honda Civic', 3),
            ('Ford Mustang', 2)
        ]
        cursor.executemany('INSERT INTO autos (modelo, disponibles) VALUES (?, ?)', autos_iniciales)
        conn.commit()
    conn.close()

from fpdf import FPDF

@app.route('/alquileres', methods=['GET'])
def get_alquileres():
    conn = get_db_connection()
    alquileres = conn.execute('SELECT * FROM alquileres').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in alquileres])

@app.route('/alquiler/<int:alquiler_id>/pdf', methods=['GET'])
def generar_pdf(alquiler_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            a.modelo,
            c.nombre,
            c.segundo_nombre,
            c.apellido,
            c.segundo_apellido,
            c.cedula,
            c.edad,
            c.direccion,
            alq.metodo_pago,
            alq.total
        FROM alquileres alq
        JOIN autos a ON alq.auto_id = a.id
        JOIN clientes c ON alq.cliente_id = c.id
        WHERE alq.id = ?
    ''', (alquiler_id,))

    alquiler = cursor.fetchone()
    conn.close()

    if not alquiler:
        return jsonify({'error': 'Alquiler no encontrado'}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Recibo de Alquiler', 0, 1, 'C')

    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, f"Modelo del auto: {alquiler['modelo']}", 0, 1)
    pdf.cell(200, 10, f"Metodo de pago: {alquiler['metodo_pago']}", 0, 1)
    pdf.cell(200, 10, f"Cliente: {alquiler['nombre']} {alquiler['segundo_nombre']} {alquiler['apellido']} {alquiler['segundo_apellido']}", 0, 1)
    pdf.cell(200, 10, f"Cedula: {alquiler['cedula']}", 0, 1)
    pdf.cell(200, 10, f"Edad: {alquiler['edad']}", 0, 1)
    pdf.cell(200, 10, f"Direccion: {alquiler['direccion']}", 0, 1)
    pdf.cell(200, 10, f"Total: ${alquiler['total']}", 0, 1)

    pdf_output = pdf.output(dest='S').encode('latin-1')

    from flask import make_response
    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=alquiler_{alquiler_id}.pdf'

    return response

if __name__ == '__main__':
    poblar_autos()
    app.run(debug=True, port=5001)
