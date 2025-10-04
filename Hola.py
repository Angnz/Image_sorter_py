import os
from openpyxl import Workbook

def carpetas_con_muchas_imagenes(ruta_base, minimo=8):
    """
    Recorre la ruta dada y:
    1. Muestra en terminal las subcarpetas con más de `minimo` imágenes.
    2. Guarda un archivo Excel (.xlsx) con esas mismas carpetas.
    """
    extensiones = {'.jpg', '.jpeg', '.heic', '.heif'}
    resultados = []

    for carpeta, _, archivos in os.walk(ruta_base):
        contador = sum(
            1
            for archivo in archivos
            if os.path.splitext(archivo)[1].lower() in extensiones
        )
        if contador > minimo:
            resultados.append([os.path.abspath(carpeta), contador])
            print(f"[{contador} imágenes] {os.path.abspath(carpeta)}")  #  Mostrar en terminal

    # Guardar Excel en la misma carpeta base
    archivo_salida = os.path.join(ruta_base, "00_carpetas_images_Index.xlsx")

    if resultados:
        wb = Workbook()
        ws = wb.active
        ws.title = "Carpetas"
        ws.append(["Carpeta", "Cantidad de imágenes"])
        for fila in resultados:
            ws.append(fila)
        wb.save(archivo_salida)
        print(f"\n Archivo Excel generado en: {archivo_salida}")
    else:
        print(f"\n No se encontraron carpetas con más de {minimo} imágenes.")

if __name__ == "__main__":
    ruta = r"E:\Bilder\Camera"   # Carpeta que quieres analizar
    carpetas_con_muchas_imagenes(ruta, minimo=8)

