import sqlite3
import os

def verificar_tablas():
    ruta_db = os.path.abspath("database/clientes_gimnasio.db")
    print(f"Conectando a: {ruta_db}")
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    print("Tablas en la base de datos:")
    for tabla in tablas:
        print(tabla[0])
    conn.close()

if __name__ == "__main__":
    verificar_tablas()