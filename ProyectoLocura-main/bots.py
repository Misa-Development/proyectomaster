import random
import string
from datetime import datetime, timedelta
from database.db import crear_tablas, conectar_db

def generar_nombre():
    nombres = ["Juan", "Ana", "Carlos", "Lucía", "Pedro", "Sofía", "Martín", "Valentina", "Diego", "Camila", "Mateo", "Julieta", "Lucas", "Mía", "Tomás", "Emma", "Facundo", "Abril", "Joaquín", "Lola"]
    return random.choice(nombres)

def generar_apellido():
    apellidos = ["Gómez", "Pérez", "Rodríguez", "López", "Fernández", "García", "Martínez", "Sánchez", "Romero", "Díaz", "Alvarez", "Torres", "Ruiz", "Ramírez", "Flores", "Acosta", "Benítez", "Molina", "Castro", "Ortiz"]
    return random.choice(apellidos)

def generar_dni():
    return str(random.randint(20000000, 49999999))

def generar_email(nombre, apellido):
    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]
    return f"{nombre.lower()}.{apellido.lower()}{random.randint(1,999)}@{random.choice(dominios)}"

def generar_fecha_nacimiento():
    hoy = datetime.now()
    edad = random.randint(16, 65)
    nacimiento = hoy - timedelta(days=edad*365 + random.randint(0, 364))
    return nacimiento.strftime("%Y-%m-%d")

def generar_sexo():
    return random.choice(["Male", "Female", "Other"])

def generar_apta_medica():
    return random.choice([0, 1])

def generar_enfermedades():
    enfermedades = ["Sin enfermedades registradas", "Hipertensión", "Diabetes", "Asma", "Alergias", "Ninguna", "Colesterol alto", "Obesidad", "Artrosis", "Migraña", ""]
    return random.choice(enfermedades)

def generar_fecha_inicio():
    hoy = datetime.now()
    inicio = hoy - timedelta(days=random.randint(0, 365*3))
    return inicio.strftime("%Y-%m-%d")

def generar_fecha_vencimiento(fecha_inicio):
    dt_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    meses = random.randint(1, 12)
    vencimiento = dt_inicio + timedelta(days=meses*30)
    return vencimiento.strftime("%Y-%m-%d")

def generar_estado():
    return random.choice([0, 1])

def generar_foto(dni):
    return None

def poblar_clientes(n=500):
    conn = conectar_db()
    cursor = conn.cursor()
    for _ in range(n):
        nombre = generar_nombre()
        apellido = generar_apellido()
        dni = generar_dni()
        email = generar_email(nombre, apellido)
        fecha_nacimiento = generar_fecha_nacimiento()
        sexo = generar_sexo()
        apta_medica = generar_apta_medica()
        enfermedades = generar_enfermedades()
        fecha_inicio = generar_fecha_inicio()
        fecha_vencimiento = generar_fecha_vencimiento(fecha_inicio)
        estado = generar_estado()
        foto = generar_foto(dni)
        cursor.execute("""
            INSERT OR IGNORE INTO clientes (nombre, apellido, dni, email, fecha_nacimiento, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento, estado, foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellido, dni, email, fecha_nacimiento, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento, estado, foto))
    conn.commit()
    conn.close()
    print(f"✅ {n} clientes insertados.")

def poblar_stock(n=20):
    productos = [
        "Proteína Whey", "Creatina", "Barra Energética", "Guantes", "Botella", "Toalla", "Cinta de correr", "Bicicleta", "Mancuernas", "Colchoneta", "Cuerda", "Banda elástica", "Esterilla", "Zapatillas", "Short deportivo", "Camiseta", "Shaker", "Gorra", "Bolso deportivo", "Suplemento multivitamínico"
    ]
    conn = conectar_db()
    cursor = conn.cursor()
    for i in range(n):
        articulo = productos[i % len(productos)]
        cantidad = random.randint(5, 100)
        monto_de_compra = round(random.uniform(100, 5000), 2)
        monto_de_venta = round(monto_de_compra * random.uniform(1.1, 2.0), 2)
        cursor.execute("""
            INSERT INTO stock (articulo, cantidad, monto_de_compra, monto_de_venta)
            VALUES (?, ?, ?, ?)
        """, (articulo, cantidad, monto_de_compra, monto_de_venta))
    conn.commit()
    conn.close()
    print(f"✅ {n} productos insertados en stock.")

if __name__ == "__main__":
    crear_tablas()
    poblar_clientes(500)
    poblar_stock(20)
