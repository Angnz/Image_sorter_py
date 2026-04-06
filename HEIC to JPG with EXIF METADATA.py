from PIL import Image
from pillow_heif import register_heif_opener
from pathlib import Path
import os
import datetime

register_heif_opener()


def obtener_ruta_sin_conflicto(ruta_destino: Path) -> Path:
    if not ruta_destino.exists():
        return ruta_destino
    carpeta = ruta_destino.parent
    nombre_base = ruta_destino.stem
    extension = ruta_destino.suffix
    contador = 1
    while True:
        nueva_ruta = carpeta / f"{nombre_base}_({contador}){extension}"
        if not nueva_ruta.exists():
            return nueva_ruta
        contador += 1


def obtener_aufnahmedatum(imagen: Image.Image):
    """
    Extrae la fecha de captura del EXIF.
    Devuelve un timestamp float, o None si no existe.
    """
    try:
        exif = imagen.getexif()
        # Tag 36867 = DateTimeOriginal, Tag 306 = DateTime (fallback)
        fecha_str = exif.get(36867) or exif.get(306)
        if fecha_str:
            dt = datetime.datetime.strptime(fecha_str, "%Y:%m:%d %H:%M:%S")
            return dt.timestamp()
    except Exception:
        pass
    return None


def convertir_heic_a_jpg(directorio_origen: str):
    directorio_origen = Path(directorio_origen)
    carpeta_jpg = directorio_origen / "JPG"
    carpeta_jpg.mkdir(exist_ok=True)

    archivos_heic = [
        f for f in directorio_origen.rglob("*")
        if f.is_file() and f.suffix.lower() in {".heic", ".heif"}
    ]

    if not archivos_heic:
        print("No se encontraron archivos HEIC/HEIF")
        return

    print(f"Se encontraron {len(archivos_heic)} archivos HEIC/HEIF\n")

    convertidos = 0

    for archivo in archivos_heic:
        try:
            imagen = Image.open(archivo)
            exif = imagen.info.get("exif")
            aufnahmedatum = obtener_aufnahmedatum(imagen)

            ruta_jpg = obtener_ruta_sin_conflicto(carpeta_jpg / f"{archivo.stem}.jpg")

            if exif:
                imagen.convert("RGB").save(ruta_jpg, "JPEG", quality=95, exif=exif)
            else:
                imagen.convert("RGB").save(ruta_jpg, "JPEG", quality=95)

            # Poner Änderungsdatum = Aufnahmedatum
            if aufnahmedatum:
                os.utime(ruta_jpg, (aufnahmedatum, aufnahmedatum))

            convertidos += 1
            print(f"✓ {archivo.name} → {ruta_jpg.name}  [{convertidos}/{len(archivos_heic)}]")

        except Exception as e:
            print(f"✗ Error al convertir {archivo.name}: {e}")

    print(f"\n✅ {convertidos}/{len(archivos_heic)} archivos convertidos")
    print(f"📁 Guardados en: {carpeta_jpg}")


if __name__ == "__main__":
    ruta = r"C:\Users\Ángel\Desktop\PIC Pauline\Orginal\Heic extraidos"
    convertir_heic_a_jpg(ruta)