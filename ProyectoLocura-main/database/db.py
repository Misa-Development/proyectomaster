import sqlite3
import os

# Conectar a la base de datos
def conectar_db():
    try:
        os.makedirs("database", exist_ok=True)
        conn = sqlite3.connect("database/clientes_gimnasio.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return None

# Crear tablas
def crear_tablas():
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            sexo TEXT NOT NULL,
            apta_medica BOOLEAN NOT NULL,
            enfermedades TEXT,
            fecha_inicio DATE NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            estado BOOLEAN NOT NULL,
            foto TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            articulo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            monto_de_compra REAL NOT NULL,
            monto_de_venta REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS historial_pagos (
            id INTEGER PRIMARY KEY,
            articulo TEXT NOT NULL,  -- <--- AGREGADO
            cliente TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha DATE NOT NULL,
            metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
            cantidad INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS historial_movimientos (
            id INTEGER PRIMARY KEY,
            tipo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT NOT NULL,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            notas TEXT  -- Nueva columna para notas
        );
    ''')
    conn.commit()
    conn.close()
    print("✅ Tablas creadas/verificadas exitosamente.")

# Obtener datos genéricos
def obtener_datos(query):
    conn = conectar_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute(query)
    datos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return datos

def obtener_clientes():
    return obtener_datos("SELECT nombre, apellido, dni, email, fecha_nacimiento, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento, estado FROM clientes")

def obtener_stock():
    return obtener_datos("SELECT articulo, cantidad, monto_de_compra, monto_de_venta FROM stock")

def obtener_historial_pagos():
    return obtener_datos("SELECT cliente, monto, fecha, metodo_pago FROM historial_pagos")

def obtener_historial_movimientos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo, nombre, apellido, dni, fecha, notas FROM historial_movimientos")
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
def obtener_ingresos():
    return obtener_datos("SELECT articulo, monto, fecha, cliente, metodo_pago, cantidad FROM historial_pagos")
# Insertar datos
# ...existing code...

def insertar_ingreso(articulo, monto, fecha, cliente, metodo_pago, cantidad):
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historial_pagos (articulo, cliente, monto, fecha, metodo_pago, cantidad) VALUES (?, ?, ?, ?, ?, ?)",
        (articulo, cliente, monto, fecha, metodo_pago, cantidad)
    )
    conn.commit()
    conn.close()
    print(f"✅ Pago registrado: {articulo} - {cliente} - {monto} - {cantidad}")
# ...existing code...
def registrar_movimiento(tipo, cliente):
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha) VALUES (?, ?, ?, ?, datetime('now'))",
                   (tipo, cliente.get("nombre", "No especificado"), cliente.get("apellido", "No especificado"), cliente.get("dni", "No especificado")))
    conn.commit()
    conn.close()
    print(f"📌 Movimiento registrado: {tipo} - {cliente['nombre']} {cliente['apellido']}")
def eliminar_cliente_por_dni(dni):
    """Elimina un cliente por su DNI después de confirmar que existe."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Buscar el cliente antes de eliminarlo
        cursor.execute("SELECT * FROM clientes WHERE dni = ?", (dni,))
        cliente_existente = cursor.fetchone()

        if not cliente_existente:
            print(f"❌ Error: No se encontró un cliente con DNI '{dni}' en la base de datos.")
            return False

        # Eliminar el cliente si existe
        cursor.execute("DELETE FROM clientes WHERE dni = ?", (dni,))
        conn.commit()

        print(f"✅ Cliente con DNI '{dni}' eliminado correctamente.")
        return True

    except sqlite3.Error as e:
        print(f"❌ Error al eliminar cliente: {e}")
        return False

    finally:
        conn.close()
if __name__ == "__main__":
    crear_tablas()