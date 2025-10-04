import os
import shutil
import hashlib
import csv

# -----------------------
# Funciones de hash y copia
# -----------------------

def calcular_hash(ruta_archivo, bloque=65536):
    """
    Calcula el hash SHA256 de un archivo para verificar duplicados.
    """
    sha256 = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        while True:
            data = f.read(bloque)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def copiar_estructura(origen, destino):
    """
    Copia la estructura completa de carpetas y archivos de 'origen' a 'destino'.
    Sobrescribe archivos si ya existen (no hay riesgo: este es el backup base).
    """
    if not os.path.exists(destino):
        os.makedirs(destino)
    for carpeta, subcarpetas, archivos in os.walk(origen):
        rel_path = os.path.relpath(carpeta, origen)
        destino_carpeta = os.path.join(destino, rel_path)
        os.makedirs(destino_carpeta, exist_ok=True)
        for archivo in archivos:
            ruta_origen = os.path.join(carpeta, archivo)
            ruta_destino = os.path.join(destino_carpeta, archivo)
            if not os.path.exists(ruta_destino):
                shutil.copy2(ruta_origen, ruta_destino)

# -----------------------
# Función CSV
# -----------------------

def generar_csv_merge(archivos_copiados, destino_merged):
    """
    Genera un CSV simple en la carpeta destino_merged con:
      - Archivo original
      - Ruta final dentro de merged
    """
    ruta_csv = os.path.join(destino_merged, "archivos_copiados.csv")
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo original", "Ruta final en merged"])
        for original, destino in archivos_copiados:
            writer.writerow([original, destino])
    print(f"\n CSV generado: {ruta_csv}")

# -----------------------
# Función principal de merge
# -----------------------

def fusionar(source, original):
    """
    Crea una nueva carpeta 'original_merged' con:
      - Todo el contenido de 'original'
      - Archivos únicos de 'source'
    La comparación se hace por hash SHA256.
    """
    base_dir = os.path.dirname(original.rstrip(os.sep))
    nombre_merged = os.path.basename(original.rstrip(os.sep)) + "_merged"
    destino_merged = os.path.join(base_dir, nombre_merged)
    os.makedirs(destino_merged, exist_ok=True)

    print(f"Copiando contenido base de '{original}' a '{destino_merged}' ...")
    copiar_estructura(original, destino_merged)

    print(f"🔍 Calculando hashes existentes en '{destino_merged}' ...")
    hashes_existentes = {}
    for carpeta, _, archivos in os.walk(destino_merged):
        for archivo in archivos:
            ruta = os.path.join(carpeta, archivo)
            try:
                h = calcular_hash(ruta)
                hashes_existentes[h] = ruta
            except Exception as e:
                print(f"Error leyendo {ruta}: {e}")

    print(f"📥 Mergeando archivos de '{source}' ...")
    nuevos = 0
    duplicados = 0
    archivos_copiados = []

    for carpeta, _, archivos in os.walk(source):
        rel_path = os.path.relpath(carpeta, source)
        destino_carpeta = os.path.join(destino_merged, rel_path)
        os.makedirs(destino_carpeta, exist_ok=True)

        for archivo in archivos:
            ruta_origen = os.path.join(carpeta, archivo)
            try:
                h = calcular_hash(ruta_origen)
                if h not in hashes_existentes:
                    shutil.copy2(ruta_origen, destino_carpeta)
                    ruta_destino_final = os.path.join(destino_carpeta, archivo)
                    hashes_existentes[h] = ruta_destino_final
                    nuevos += 1
                    archivos_copiados.append((ruta_origen, ruta_destino_final))
                    print(f"➕ Copiado: {ruta_origen}")
                else:
                    duplicados += 1
            except Exception as e:
                print(f"Error procesando {ruta_origen}: {e}")

    # Generar CSV de archivos copiados
    generar_csv_merge(archivos_copiados, destino_merged)

    print("\n ¡Proceso completado!")
    print(f" Archivos nuevos copiados: {nuevos}")
    print(f" Archivos duplicados ignorados: {duplicados}")
    print(f" Carpeta final de prueba: {destino_merged}")

# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":
    # 🔧 Configura estas rutas antes de ejecutar
    source_path   = r"E:\Check_Camera\sorted\2024"        # Carpeta origen (source)
    original_path = r"C:\Users\Ángel\Pictures\2024"      # Carpeta original (no se modifica, definitivas)

    fusionar(source_path, original_path)

