#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import traceback

try:
    print("🔄 Iniciando test de la aplicación...")
    
    # Test 1: Import de módulos
    print("1. Probando imports...")
    from database.db import conectar_db
    print("   ✅ database.db importado correctamente")
    
    # Test 2: Context manager
    print("2. Probando context manager...")
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"   ✅ Context manager funciona: {result}")
    
    # Test 3: Import de la aplicación
    print("3. Probando import de app.py...")
    import V1.app as app
    print("   ✅ app.py importado correctamente")
    
    print("🎉 Todos los tests pasaron!")
    
except Exception as e:
    print(f"❌ Error en el test: {e}")
    print("Detalles del error:")
    traceback.print_exc()
    sys.exit(1)
