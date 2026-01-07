from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .session import engine, Base


class Usuarios(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String, unique=True, nullable=False)

    cartas = relationship("UsuarioCarta", back_populates="usuario", cascade="all, delete")


class Cartas(Base):
    __tablename__ = "Cartas"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_api = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    type = Column(String)
    price = Column(Float)
    rarity = Column(String)
    number = Column(String)
    set_id = Column(String)
    set_name = Column(String)
    stage = Column(String)
    especial_type = Column(String)
    trainer = Column(String)
    edition = Column(String)

    usuarios = relationship("UsuarioCarta", back_populates="carta", cascade="all, delete")


class UsuarioCarta(Base):
    __tablename__ = "usuario_carta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_nombre = Column(String, ForeignKey("Usuarios.nombre", ondelete="CASCADE"), nullable=False)
    carta_id = Column(String, ForeignKey("Cartas.id_api", ondelete="CASCADE"), nullable=False)
    # nombre_pokemon = Column(String)  # solo info adicional

    usuario = relationship("Usuarios", back_populates="cartas", foreign_keys=[usuario_nombre])
    carta = relationship("Cartas", back_populates="usuarios", foreign_keys=[carta_id])

Base.metadata.create_all(bind=engine)