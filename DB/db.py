import sqlite3

def conectar_db():
    conn = sqlite3.connect('database/lubricentro.db')
    return conn

def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        telefono TEXT NOT NULL
                    )''')
    # Agrega más tablas según sea necesario
    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
