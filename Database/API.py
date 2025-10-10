import requests
import Database.tablas as sql
import time

"""
ESTA API SIRVE PARA OBTENER LOS POKEMONES, 
Y EL CODIGO DE ESTE ARCHIVO SIRVE PARA SOLICITAR 
TODOS LOS POKEMONES QUE TIENE DISPONIBLE LA API
"""

page = 1
total_guardadas = 0

while True:
    url = f"https://api.pokemontcg.io/v2/cards?page={page}&pageSize=250"
    headers = {"X-Api-Key": "TU_API_KEY"}  # Solo si la necesitas
    response = requests.get(url, headers=headers)
    data = response.json()

    cartas = data.get("data", [])
    if not cartas:
        break  # Ya no hay más cartas

    for i, carta in enumerate(cartas):
        time.sleep(0.6)
        print(i)

        id_api = carta.get("id")
        nombre = carta.get("name")
        tipos = carta.get("types", [])
        tipo = tipos[0] if tipos else "Desconocido"
        rareza = carta.get("rarity", "Desconocida")

        precios = carta.get("tcgplayer", {}).get("prices", {})
        precio = precios.get("market", precios.get("normal", {})).get("market", 0.0)

        # Nuevos campos
        numero = carta.get("number", "N/A")
        set_info = carta.get("set", {})
        set_id = set_info.get("id", "N/A")
        set_nombre = set_info.get("name", "N/A")

        subtipos = carta.get("subtypes", [])

        stage = subtipos[0] if subtipos else "Ninguno"
        especial_type = subtipos[1] if len(subtipos) > 1 else "Normal"
        trainer = subtipos[2] if len(subtipos) > 2 else "Desconocido"
        edition = subtipos[3] if len(subtipos) > 3 else "Ninguno"

        # Guardar en base de datos
        try:
            sql.cursor.execute("""
                INSERT OR IGNORE INTO Cartas (id_api, nombre, type, price, rarity, number, set_id, set_name, stage, especial_type, trainer, edition)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_api, nombre, tipo, precio, rareza, numero, set_id, set_nombre, stage, especial_type, trainer, edition))
            sql.conn.commit()
            total_guardadas += 1
        except Exception as e:
            print(f"Error guardando {id_api}: {e}")

        

    print(f"Página {page} procesada. Cartas totales: {total_guardadas}")
    page += 1