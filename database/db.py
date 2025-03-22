import sqlite3
import os

# Función para conectar a la base de datos
def conectar_db():
    # Asegurar que el directorio existe
    if not os.path.exists("database"):
        os.makedirs("database")
    
    # Conexión a la base de datos (clientes de gimnasio)
    conn = sqlite3.connect('database/clientes_gimnasio.db')
    return conn

# Función para crear tablas
def crear_tablas():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Crear tabla clientes con todos los campos necesarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                edad INTEGER NOT NULL,
                sexo TEXT NOT NULL,
                apta_medica BOOLEAN NOT NULL,
                enfermedades TEXT,
                fecha_inicio DATE NOT NULL,
                fecha_vencimiento DATE NOT NULL
            )
        ''')
        
        conn.commit()
        print("Tablas creadas o verificadas exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        if conn:
            conn.close()

# Función para insertar datos de prueba
def insertar_clientes():
    clientes = [
        {"nombre": "Juan", "apellido": "Pérez", "dni": "12345678", "email": "juan.perez@gmail.com", "edad": 25, "sexo": "Masculino", "apta_medica": True, "enfermedades": "Ninguna", "fecha_inicio": "2023-01-01", "fecha_vencimiento": "2024-01-01"},
        {"nombre": "María", "apellido": "Gómez", "dni": "23456789", "email": "maria.gomez@gmail.com", "edad": 30, "sexo": "Femenino", "apta_medica": False, "enfermedades": "Asma", "fecha_inicio": "2023-02-15", "fecha_vencimiento": "2024-02-15"},
    ]
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Insertar clientes
        for cliente in clientes:
            cursor.execute('''
                INSERT OR IGNORE INTO clientes (nombre, apellido, dni, email, edad, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cliente["nombre"], cliente["apellido"], cliente["dni"], cliente["email"], cliente["edad"], cliente["sexo"], cliente["apta_medica"], cliente["enfermedades"], cliente["fecha_inicio"], cliente["fecha_vencimiento"]))
        
        conn.commit()
        print("Clientes insertados exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al insertar clientes: {e}")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    crear_tablas()
    insertar_clientes()