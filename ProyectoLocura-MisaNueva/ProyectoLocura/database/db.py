import sqlite3
import os

# Función para conectar a la base de datos
def conectar_db():
    # Garantiza que el directorio de la base de datos exista
    if not os.path.exists("database"):
        os.makedirs("database")
    # Establece la conexión con la base de datos
    conn = sqlite3.connect("database/clientes_gimnasio.db")
    conn.row_factory = sqlite3.Row  # Configurar filas como diccionarios
    return conn

# Función para verificar la existencia de la tabla
def verificar_existencia_tabla(nombre_tabla):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nombre_tabla}'")
        if cursor.fetchone():
            print(f"La tabla '{nombre_tabla}' existe en la base de datos.")
        else:
            print(f"La tabla '{nombre_tabla}' NO existe.")
    except sqlite3.Error as e:
        print(f"Error al verificar la tabla '{nombre_tabla}': {e}")
    finally:
        if conn:
            conn.close()

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

        # Crear tabla ingresos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                articulo TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha DATE NOT NULL,
                cliente TEXT NOT NULL,
                metodo_pago TEXT NOT NULL DEFAULT 'Efectivo'
            )
        ''')

        # Crear tabla stock
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                articulo TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                monto_de_compra REAL NOT NULL,
                monto_de_venta REAL NOT NULL
            )
        ''')

        conn.commit()
        print("Tablas creadas o verificadas exitosamente.")

        # Verificar que la tabla 'stock' exista
        verificar_existencia_tabla("stock")

    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        if conn:
            conn.close()

# Función para insertar un ingreso en la tabla ingresos
def insertar_ingreso(articulo, monto, fecha, cliente, metodo_pago):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO ingresos (articulo, monto, fecha, cliente, metodo_pago)
            VALUES (?, ?, ?, ?, ?)
        ''', (articulo, monto, fecha, cliente, metodo_pago))

        conn.commit()
        print("Ingreso registrado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al insertar ingreso: {e}")
    finally:
        if conn:
            conn.close()

# Función para insertar un artículo en la tabla stock
def insertar_stock(articulo, cantidad, monto_de_compra, monto_de_venta):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO stock (articulo, cantidad, monto_de_compra, monto_de_venta)
            VALUES (?, ?, ?, ?)
        ''', (articulo, cantidad, monto_de_compra, monto_de_venta))

        conn.commit()
        print("Stock registrado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al insertar stock: {e}")
    finally:
        if conn:
            conn.close()
def obtener_clientes():
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, apellido, sexo, edad, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento, activo
            FROM clientes
        ''')
        clientes = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error al obtener clientes: {e}")
        clientes = []
    finally:
        conn.close()
    return clientes
# Función para obtener los ingresos registrados
def obtener_ingresos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT articulo, monto, fecha, cliente, metodo_pago
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

# Función para obtener el stock registrado
def obtener_stock():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT articulo, cantidad, monto_de_compra, monto_de_venta
            FROM stock
        ''')
        stock = [dict(row) for row in cursor.fetchall()]
        return stock
    except sqlite3.Error as e:
        print(f"Error al obtener el stock: {e}")
        return []
    finally:
        if conn:
            conn.close()
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