"""Script para migrar datos desde un archivo sqlite de respaldo hacia la base de datos del proyecto.

Uso:
    python scripts/migrate_from_backup.py <ruta_al_respaldo>

Lo que hace:
- Hace una copia de seguridad del archivo `PokeDatabase.db` actual (por seguridad)
- Adjunta la DB de respaldo y copia las tablas `Usuarios`, `Cartas` y `usuario_carta`
  usando `INSERT OR IGNORE` para evitar duplicados.

Notas:
- Asegúrate de que las tablas del respaldo tengan los mismos nombres y columnas.
- Revisa el archivo de salida y los logs (se imprime en consola).
"""

import sys
import os
import shutil
import sqlite3
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DB = os.path.join(PROJECT_ROOT, "PokeDatabase.db")


def backup_current_db():
    if not os.path.exists(CURRENT_DB):
        print("No se encontró la base de datos actual:", CURRENT_DB)
        return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = CURRENT_DB + f".backup_{ts}"
    shutil.copy2(CURRENT_DB, dest)
    print("Copia de seguridad creada en:", dest)
    return dest


def migrate_from_backup(backup_path):
    if not os.path.exists(backup_path):
        print("El archivo de respaldo no existe:", backup_path)
        return False

    # Hacer backup del DB actual antes de modificar
    backup_current_db()

    conn = sqlite3.connect(CURRENT_DB)
    cur = conn.cursor()

    try:
        # ATTACH backup
        cur.execute("ATTACH DATABASE ? AS bck", (backup_path,))
        print("Adjuntada DB de respaldo como 'bck'")

        tables = ["Usuarios", "Cartas", "usuario_carta"]
        for t in tables:
            # Verificar que la tabla exista en la DB de respaldo
            cur.execute("SELECT name FROM bck.sqlite_master WHERE type='table' AND name=?", (t,))
            if not cur.fetchone():
                print(f"Tabla '{t}' no encontrada en el respaldo. Se omite.")
                continue

            sql = f"INSERT OR IGNORE INTO main.{t} SELECT * FROM bck.{t};"
            print("Ejecutando:", sql)
            cur.execute(sql)

        conn.commit()
        print("Migración completada. Se copiaron las tablas indicadas (si existían).")
    except Exception as e:
        print("Error durante la migración:", e)
        conn.rollback()
        return False
    finally:
        try:
            cur.execute("DETACH DATABASE bck")
        except Exception:
            pass
        conn.close()

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python scripts/migrate_from_backup.py <ruta_al_respaldo>")
        sys.exit(1)

    backup_path = sys.argv[1]
    ok = migrate_from_backup(backup_path)
    sys.exit(0 if ok else 2)
