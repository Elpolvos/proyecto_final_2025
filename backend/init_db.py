import sqlite3

def init_db():
    conn = sqlite3.connect('backend/database.db')
    print("Opened database successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        segundo_nombre TEXT,
        apellido TEXT NOT NULL,
        segundo_apellido TEXT,
        cedula TEXT NOT NULL UNIQUE,
        edad INTEGER,
        direccion TEXT
    )
    ''')
    print("Table 'clientes' created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS autos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        disponibles INTEGER NOT NULL
    )
    ''')
    print("Table 'autos' created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS alquileres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auto_id INTEGER,
        cliente_id INTEGER,
        metodo_pago TEXT,
        total REAL,
        FOREIGN KEY(auto_id) REFERENCES autos(id),
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    ''')
    print("Table 'alquileres' created successfully")
    conn.close()

if __name__ == '__main__':
    init_db()
