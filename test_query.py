import sqlite3

conn = sqlite3.connect("database/clientes_gimnasio.db")
cursor = conn.cursor()

cursor.execute("SELECT dni, nombre, apellido FROM clientes")
clientes = cursor.fetchall()

print("📋 Lista de DNIs en la base de datos:")
for cliente in clientes:
    print(f"[{cliente[0]}] - {cliente[1]} {cliente[2]}")  # Muestra el DNI con corchetes para ver espacios extra

conn.close()