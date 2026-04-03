import os
import shutil

# -----------------------
#Busca todos los archivos HEIC o HEIF de una carpeta y susu subcarpetas y las COPIA a una nueva carpeta llamada "Heic extraidos" dentro de la carpeta original. Evita sobrescribir archivos agregando _(1), _(2), etc. al nombre.
# -----------------------

def obtener_ruta_sin_conflicto(ruta_destino):
    if not os.path.exists(ruta_destino):
        return ruta_destino

    carpeta, nombre = os.path.split(ruta_destino)
    nombre_base, extension = os.path.splitext(nombre)

    contador = 1
    while True:
        nuevo_nombre = f"{nombre_base}_({contador}){extension}"
        nueva_ruta = os.path.join(carpeta, nuevo_nombre)

        if not os.path.exists(nueva_ruta):
            return nueva_ruta

        contador += 1


def extraer_heic(ruta_origen):
    extensiones_heic = {'.heic', '.heif'}

    carpeta_destino = os.path.join(ruta_origen, "Heic extraidos")
    os.makedirs(carpeta_destino, exist_ok=True)

    total = 0

    for carpeta, _, archivos in os.walk(ruta_origen):
        # Evitar procesar la carpeta destino
        if os.path.abspath(carpeta) == os.path.abspath(carpeta_destino):
            continue

        for archivo in archivos:
            extension = os.path.splitext(archivo)[1].lower()

            if extension in extensiones_heic:
                ruta_original = os.path.join(carpeta, archivo)
                ruta_destino = os.path.join(carpeta_destino, archivo)

                ruta_destino = obtener_ruta_sin_conflicto(ruta_destino)

                shutil.copy2(ruta_original, ruta_destino)

                total += 1
                print(f"{total} Copiado: {ruta_original} → {ruta_destino}")

    print("\n✅ Proceso terminado")
    print(f"Total archivos HEIC/HEIF copiados: {total}")


# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":
    ruta = r"C:\Users\Ángel\Desktop\PIC Pauline\Orginal"  # 👈 Aqui va la ruta

    if not os.path.exists(ruta):
        print("❌ La ruta no existe")
    else:
        extraer_heic(ruta)
