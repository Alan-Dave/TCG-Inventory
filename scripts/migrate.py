import sqlite3
from sqlalchemy.orm import Session
from session import engine
from models import Cartas
# Conectar a BD antigua
old_conn = sqlite3.connect("PokeDatabase_old.db")
old_cursor = old_conn.cursor()

# Leer cartas de la BD antigua
old_cursor.execute("SELECT id_api, nombre, type, price, rarity, number, set_id, set_name, stage, especial_type, trainer, edition FROM Cartas")
cartas_old = old_cursor.fetchall()

session = Session(bind=engine)

total = 0

for row in cartas_old:
    carta = Cartas(
        id_api=row[0],
        nombre=row[1],
        type=row[2],
        price=row[3],
        rarity=row[4],
        number=row[5],
        set_id=row[6],
        set_name=row[7],
        stage=row[8],
        especial_type=row[9],
        trainer=row[10],
        edition=row[11]
    )
    
    session.add(carta)
    total += 1
    
    # Commit cada 500 para no petar la RAM
    if total % 500 == 0:
        session.commit()
        print(f"✅ {total} cartas migradas...")

session.commit()
print(f"🎉 Migración completa: {total} cartas importadas")
