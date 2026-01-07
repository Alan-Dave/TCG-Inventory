import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


# Define la ruta a la carpeta de imágenes
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images"))

# Asegurarnos que la carpeta existe
os.makedirs(IMAGES_DIR, exist_ok=True)


def get_pixmap_from_zip(relative_path, size=None, id_api=None):
    """
    Carga una imagen desde la carpeta assets/images y la retorna como QPixmap.
    
    Args:
        relative_path: Nombre del archivo (ej: 'pikachu.jpg' o 'pikachu')
        size: Tupla opcional (width, height) para escalar manteniendo proporción
        id_api: ID opcional de la PokeAPI para buscar imágenes con formato nombre_id
    
    Returns:
        QPixmap o None si no se encuentra/falla la carga
    """
    try:
        print(f"\nBuscando imagen: {relative_path}")
        print(f"Directorio de imágenes: {IMAGES_DIR}")
        
        if not os.path.isdir(IMAGES_DIR):
            print("❌ El directorio de imágenes no existe")
            return None

        # Normalizar el nombre
        rel_path = relative_path.replace('\\', '/').lstrip('/')
        base_name = os.path.basename(rel_path)
        name_no_ext, ext = os.path.splitext(base_name)
        
        # Limpiar el nombre para búsqueda
        clean_name = name_no_ext.lower().replace(' ', '_')
        
        # Construir lista de posibles nombres
        candidates = []
        
        # 1. Si tenemos el ID, intentar primero con nombre_id
        if id_api:
            for ext in ['.webp', '.png', '.jpg', '.jpeg']:
                candidates.append(os.path.join(IMAGES_DIR, f"{clean_name}_{id_api}{ext}"))
        
        # 2. Intentar con el nombre exacto si tiene extensión
        if ext:
            candidates.append(os.path.join(IMAGES_DIR, base_name))
            
        # 3. Probar con diferentes extensiones (sin ID)
        for ext in ['.webp', '.png', '.jpg', '.jpeg']:
            candidates.append(os.path.join(IMAGES_DIR, f"{clean_name}{ext}"))

        # 3. Buscar en el directorio de imágenes
        found = None
        for cand in candidates:
            print(f"Probando: {cand}")
            if os.path.exists(cand) and os.path.isfile(cand):
                print(f"✅ Imagen encontrada: {cand}")
                found = cand
                break
                
        # 4. Si no se encuentra, hacer búsqueda insensible a mayúsculas/minúsculas
        if not found:
            print("Realizando búsqueda insensible a mayúsculas/minúsculas...")
            for root, _, files in os.walk(IMAGES_DIR):
                for f in files:
                    f_lower = f.lower()
                    if (f_lower == base_name.lower() or 
                        f_lower.startswith(clean_name + '.')):
                        found = os.path.join(root, f)
                        print(f"✅ Imagen encontrada (case-insensitive): {found}")
                        break
                if found:
                    break

        # 5. Cargar y retornar el pixmap
        if not found:
            print("❌ No se encontró ninguna imagen")
            return None

        print(f"Cargando imagen: {found}")
        pix = QPixmap(found)
        
        if pix.isNull():
            print("❌ Error al cargar la imagen en QPixmap")
            return None
            
        print(f"✅ Imagen cargada exitosamente: {pix.width()}x{pix.height()}")
        
        # Escalar si se especifica un tamaño
        if size:
            pix = pix.scaled(
                size[0], size[1], 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            print(f"   Escalada a: {pix.width()}x{pix.height()}")
            
        return pix
        
    except Exception as e:
        print(f"❌ Error al procesar la imagen: {str(e)}")
        return None
