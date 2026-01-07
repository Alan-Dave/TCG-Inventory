import requests
import time
from MyQtApp.session import SessionLocal
from MyQtApp.models import Cartas

session = SessionLocal()

page = 1
total_guardadas = 0

while True:
    url = f"https://api.pokemontcg.io/v2/cards?page={page}&pageSize=250"
    headers = {"X-Api-Key": "TU_API_KEY"}  # solo si tu API la requiere
    response = requests.get(url, headers=headers)
    data = response.json()

    cartas = data.get("data", [])
    if not cartas:
        break

    for i, carta in enumerate(cartas):
        time.sleep(0.6)
        print(f"Procesando carta {i}")

        id_api = carta.get("id")
        nombre = carta.get("name")
        tipos = carta.get("types", [])
        tipo = tipos[0] if tipos else "Desconocido"
        rareza = carta.get("rarity", "Desconocida")

        precios = carta.get("tcgplayer", {}).get("prices", {})
        precio = precios.get("market", precios.get("normal", {})).get("market", 0.0)

        numero = carta.get("number", "N/A")
        set_info = carta.get("set", {})
        set_id = set_info.get("id", "N/A")
        set_nombre = set_info.get("name", "N/A")

        subtipos = carta.get("subtypes", [])
        stage = subtipos[0] if subtipos else "Ninguno"
        especial_type = subtipos[1] if len(subtipos) > 1 else "Normal"
        trainer = subtipos[2] if len(subtipos) > 2 else "Desconocido"
        edition = subtipos[3] if len(subtipos) > 3 else "Ninguno"

        try:
            # Verificar si ya existe
            existe = session.query(Cartas).filter_by(id_api=id_api).first()
            if existe:
                continue

            nueva_carta = Cartas(
                id_api = id_api, nombre=nombre, type=tipo, price=precio,
                rarity = rareza, number=numero, set_id=set_id,
                set_name = set_nombre, stage=stage, especial_type=especial_type,
                trainer = trainer, edition=edition
            )

            session.add(nueva_carta)
            session.commit()
            total_guardadas += 1

        except Exception as e:
            session.rollback()
            print(f"Error guardando {id_api}: {e}")

    print(f"Página {page} procesada ✅ | Cartas totales guardadas: {total_guardadas}")
    page += 1

session.close()
print(f"IMPORTACIÓN FINALIZADA ✅ Total insertadas: {total_guardadas}")
