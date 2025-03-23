import sqlite3
import os

# Función para conectar a la base de datos
def conectar_db():
    # Asegurar que el directorio existe
    if not os.path.exists("database"):
        os.makedirs("database")
    
    # Conexión a la base de datos (clientes de gimnasio)
    conn = sqlite3.connect("database/clientes_gimnasio.db")
    conn.row_factory = sqlite3.Row  # Configurar filas como diccionarios
    return conn

# Función para crear tablas
def crear_tablas():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Crear tabla clientes
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

        # Crear tabla historial_pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha_pago DATE NOT NULL,
                metodo_pago TEXT NOT NULL
            )
        ''')

        # Crear tabla ingresos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                articulo TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha DATE NOT NULL,
                cliente TEXT NOT NULL
            )
        ''')

        conn.commit()
        print("Tablas creadas o verificadas exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        if conn:
            conn.close()

# Función para insertar datos de prueba en la tabla clientes
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

# Función para insertar datos de prueba en la tabla historial_pagos
def insertar_historial_pagos():
    pagos = [
        {"cliente": "Juan", "monto": 500.0, "fecha_pago": "2023-01-15", "metodo_pago": "Efectivo"},
        {"cliente": "María", "monto": 700.0, "fecha_pago": "2023-02-20", "metodo_pago": "Tarjeta"},
    ]
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Insertar pagos
        for pago in pagos:
            cursor.execute('''
                INSERT INTO historial_pagos (cliente, monto, fecha_pago, metodo_pago)
                VALUES (?, ?, ?, ?)
            ''', (pago["cliente"], pago["monto"], pago["fecha_pago"], pago["metodo_pago"]))
        
        conn.commit()
        print("Historial de pagos insertado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al insertar pagos: {e}")
    finally:
        if conn:
            conn.close()

# Función para insertar un ingreso en la tabla ingresos
def insertar_ingreso(articulo, monto, fecha, cliente):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ingresos (articulo, monto, fecha, cliente)
            VALUES (?, ?, ?, ?)
        ''', (articulo, monto, fecha, cliente))
        
        conn.commit()
        print("Ingreso registrado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al insertar ingreso: {e}")
    finally:
        if conn:
            conn.close()

# Función para obtener los ingresos registrados
def obtener_ingresos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT articulo, monto, fecha, cliente 
            FROM ingresos
        ''')
        ingresos = [dict(row) for row in cursor.fetchall()]
        return ingresos
    except sqlite3.Error as e:
        print(f"Error al obtener los ingresos: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Función para obtener el historial de pagos
def obtener_historial_pagos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cliente, monto, fecha_pago, metodo_pago 
            FROM historial_pagos
        ''')
        pagos = [dict(row) for row in cursor.fetchall()]
        return pagos
    except sqlite3.Error as e:
        print(f"Error al obtener el historial de pagos: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    crear_tablas()
    insertar_clientes()
    insertar_historial_pagos()