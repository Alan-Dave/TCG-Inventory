import sqlite3 as sql


# Conexión
conn = sql.connect("mi_base.db")
cursor = conn.cursor()

# Crear tabla
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre TEXT UNIQUE NOT NULL
    );
''')

cursor.execute("""CREATE TABLE IF NOT EXISTS Cartas (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    id_api TEXT UNIQUE NOT NULL, -- ← esto asegura que no se repita
    nombre TEXT NOT NULL,
    type TEXT,
    price REAL,
    rarity TEXT,
    number TEXT,
    set_id TEXT,
    set_name TEXT,
    stage TEXT,
    especial_type TEXT,
    trainer TEXT,
    edition TEXT
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS usuario_carta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_nombre TEXT NOT NULL,
    carta_id TEXT NOT NULL,
    nombre_pokemon TEXT NOT NULL,
    FOREIGN KEY (usuario_nombre) REFERENCES Usuarios(nombre) ON DELETE CASCADE,
    FOREIGN KEY (carta_id) REFERENCES Cartas(id_api) ON DELETE CASCADE,
    FOREIGN KEY (nombre_pokemon) REFERENCES Cartas(nombre) ON DELETE CASCADE,
    UNIQUE(usuario_nombre, carta_id) -- evita que el mismo usuario tenga duplicada la carta
               );""")

conn.commit()