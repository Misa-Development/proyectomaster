import flet as ft
import sqlite3
import datetime
import time
from database.db import conectar_db
import threading

# ---------------------------------------------------------------------------
# Función para obtener el número de clientes activos.
def obtener_clientes_activos():
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM clientes WHERE estado = 1")
        total_activos = cursor.fetchone()["total"]
    except sqlite3.Error as e:
        print(f"⚠️ Error al obtener clientes activos: {e}")
        total_activos = 0
    finally:
        if conn:
            conn.close()
    return total_activos

# ---------------------------------------------------------------------------
# Función para obtener próximas renovaciones.
def obtener_proximas_renovaciones():
    total_renovaciones = 0
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha_vencimiento, estado FROM clientes WHERE estado = 1")
        registros = cursor.fetchall()
        fecha_actual = datetime.datetime.now().date()
        for registro in registros:
            fecha_str = registro["fecha_vencimiento"]
            fecha_obj = None
            formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
            for fmt in formatos:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, fmt).date()
                    break
                except ValueError:
                    continue
            if fecha_obj is None:
                print(f"  -> Formato de fecha no reconocido para ID {registro['id']}: {fecha_str}")
                continue

            diff = (fecha_obj - fecha_actual).days
            if 0 < diff <= 15:
                total_renovaciones += 1

    except sqlite3.Error as e:
        print(f"⚠️ Error al obtener próximas renovaciones: {e}")
        total_renovaciones = 0
    finally:
        if conn:
            conn.close()

    return total_renovaciones

# ---------------------------------------------------------------------------
# Función para obtener clientes vencidos.
def obtener_clientes_vencidos():
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        fecha_actual = datetime.datetime.now().date()

        cursor.execute("SELECT id, fecha_vencimiento FROM clientes")
        registros = cursor.fetchall()

        total_renovaciones = 0

        for registro in registros:
            cliente_id = registro["id"]
            fecha_vencimiento_str = registro["fecha_vencimiento"]

            fecha_vencimiento_obj = None
            formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
            for fmt in formatos:
                try:
                    fecha_vencimiento_obj = datetime.datetime.strptime(fecha_vencimiento_str, fmt).date()
                    break
                except ValueError:
                    continue

            if fecha_vencimiento_obj is None:
                continue

            if fecha_vencimiento_obj <= fecha_actual:
                diferencia_dias = (fecha_actual - fecha_vencimiento_obj).days
                if diferencia_dias <= 15:
                    total_renovaciones += 1

    except sqlite3.Error as e:
        print(f"⚠️ Error al obtener clientes vencidos: {e}")
        total_renovaciones = 0
    finally:
        if conn:
            conn.close()

    return total_renovaciones

# ---------------------------------------------------------------------------
# Función para obtener fecha y hora actual (ahora con segundos).
def obtener_fecha_hora_actual():
    ahora = datetime.datetime.now()
    fechaoficial = ahora.strftime("%d-%m-%Y")
    horaoficial = ahora.strftime("%H:%M:%S")  # <-- Ahora incluye los segundos
    return fechaoficial, horaoficial