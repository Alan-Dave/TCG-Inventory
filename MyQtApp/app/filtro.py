from sqlalchemy.orm import Session
from models import Cartas, UsuarioCarta

def filtro_cartas_sqlalchemy(
        session: Session,
        user,
        id_api=None, nPokemon=None, tipo=None, precio=None, rareza=None,
        number=None, set_id=None, set_name=None, stage=None, especial_type=None,
        trainer=None, edition=None
    ):

    # Filtros dinámicos según tu diccionario original
    filtros = {
        "id_api": id_api,
        "nombre": nPokemon,
        "type": tipo,
        "price": precio,
        "rarity": rareza,
        "number": number,
        "set_id": set_id,
        "set_name": set_name,
        "stage": stage,
        "especial_type": especial_type,
        "trainer": trainer,
        "edition": edition
    }

    campos_like = ["nombre", "type", "rarity", "edition", "set_name", "especial_type", "trainer"]

    # Query base con JOIN a la tabla intermedia
    query = (
        session.query(Cartas)
        .join(UsuarioCarta, Cartas.id_api == UsuarioCarta.carta_id)
        .filter(UsuarioCarta.usuario_nombre == user)
    )

    # Construcción de filtros dinámicos
    for campo, valor in filtros.items():
        if valor not in (None, "", []):
            columna = getattr(Cartas, campo)
            if campo in campos_like:
                query = query.filter(columna.ilike(f"%{valor}%"))
            else:
                query = query.filter(columna == valor)

    resultados = query.all()

    for carta in resultados:
        print(
            f"{carta.nombre} | ID: {carta.id_api} | Tipo: {carta.type} | Precio: {carta.price}"
        )

    return resultados
