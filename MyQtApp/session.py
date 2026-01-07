from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtener la ruta absoluta al directorio del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "PokeDatabase.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"Usando base de datos en: {DB_PATH}")

engine = create_engine(DATABASE_URL, echo=True)  # Activamos echo para ver las consultas SQL

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Asegurarse de que todas las tablas existan
from . import models  # Importamos los modelos aquí para evitar importación circular
Base.metadata.create_all(bind=engine)