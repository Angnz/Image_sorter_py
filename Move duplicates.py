import os
import hashlib
import shutil

# -----------------------
# CONFIG
# -----------------------

ruta_root = r"C:\Users\Ángel\Desktop\Fotos_new"

# -----------------------
# HASH
# -----------------------

def calcular_hash(ruta, bloque=65536):
    sha256 = hashlib.sha256()
    with open(ruta, "rb") as f:
        while True:
            data = f.read(bloque)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


# -----------------------
# MAIN
# -----------------------

hashes = {}
duplicados = 0

for carpeta, _, archivos in os.walk(ruta_root):

    # evitar procesar carpetas de duplicados
    if "_duplicates_" in carpeta:
        continue

    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)

        try:
            h = calcular_hash(ruta)

            if h in hashes:
                # 📁 carpeta local de duplicados
                carpeta_dup = os.path.join(carpeta, "_duplicates_")
                os.makedirs(carpeta_dup, exist_ok=True)

                destino = os.path.join(carpeta_dup, archivo)

                # evitar conflictos de nombre
                base, ext = os.path.splitext(destino)
                i = 1
                while os.path.exists(destino):
                    destino = f"{base}_({i}){ext}"
                    i += 1

                shutil.move(ruta, destino)

                duplicados += 1
                print(f"🗑️ Duplicado movido: {ruta}")

            else:
                hashes[h] = ruta

        except Exception as e:
            print(f"Error con {ruta}: {e}")

print(f"\n✅ Duplicados movidos: {duplicados}")