import os
import shutil
from datetime import datetime

# ── RUTAS ──────────────────────────────────────────────────────────────────────
FUENTES = [
    r"C:\Users\Angel\Pictures\Whatsapp_S9\Videos",
    r"C:\Users\Angel\Pictures\Whatsapp_S9\Fotos",
]
DESTINO = r"E:\Bilder\Whatsapp_backup"

# ── CREAR DESTINO SI NO EXISTE ─────────────────────────────────────────────────
os.makedirs(DESTINO, exist_ok=True)

# ── COPIA RECURSIVA (sin sobreescribir ni borrar) ──────────────────────────────
copiados    = []
omitidos    = []
errores     = []
inicio      = datetime.now()
fecha_hoy   = inicio.strftime("%d/%m/%Y")
hora_inicio = inicio.strftime("%H:%M:%S")
mes_ano     = inicio.strftime("%Y_%m")

REPORTE = rf"E:\Bilder\Whatsapp_backup\backup_whatsapp_reporte_{mes_ano}.txt"

for carpeta_origen in FUENTES:
    if "Fotos" in carpeta_origen:
        nombre_subcarpeta = "WhatsApp Images"
    elif "Videos" in carpeta_origen:
        nombre_subcarpeta = "WhatsApp Video"
    else:
        nombre_subcarpeta = os.path.basename(carpeta_origen)

    if not os.path.exists(carpeta_origen):
        errores.append(f"[CARPETA NO ENCONTRADA] {carpeta_origen}")
        continue

    try:
        walker = list(os.walk(carpeta_origen))
    except PermissionError as e:
        errores.append(f"[SIN PERMISO] {carpeta_origen}: {e}")
        continue

    for raiz, subcarpetas, archivos in walker:
        ruta_relativa   = os.path.relpath(raiz, carpeta_origen)
        carpeta_destino = os.path.join(DESTINO, nombre_subcarpeta, ruta_relativa)
        os.makedirs(carpeta_destino, exist_ok=True)

        for archivo in archivos:                                          
            origen   = os.path.join(raiz, archivo)
            destino  = os.path.join(carpeta_destino, archivo)
            ruta_log = os.path.join(nombre_subcarpeta, ruta_relativa, archivo)

            #added a format and file SIze in the report
            if os.path.exists(destino):
                omitidos.append(ruta_log)
            else:
                try:
                    shutil.copy2(origen, destino)
                    # ✅ tamaño legible
                    tam = os.path.getsize(origen)
                    if tam < 1024:
                        tam_str = f"{tam} B"
                    elif tam < 1024 ** 2:
                        tam_str = f"{tam / 1024:.1f} KB"
                    else:
                        tam_str = f"{tam / 1024 ** 2:.1f} MB"
                    copiados.append(f"{ruta_log}  ({tam_str})")
                except Exception as e:
                    errores.append(f"{ruta_log}: {e}")

# ── REPORTE ────────────────────────────────────────────────────────────────────
fin      = datetime.now()
hora_fin = fin.strftime("%H:%M:%S")
duracion = int((fin - inicio).total_seconds())

lineas = [
    "=" * 55,
    f"  BACKUP WHATSAPP — {fecha_hoy}",
    "=" * 55,
    f"  Inicio : {hora_inicio}   |   Fin: {hora_fin}",
    f"  ⏱️  Duración total                  : {duracion} segundos",
    f"  Destino: {DESTINO}",
    "-" * 55,
    f"  ✅  Archivos NUEVOS copiados hoy   : {len(copiados)}",
    f"  ⏭️  Archivos ya existentes (omitidos): {len(omitidos)}",
    f"  ❌  Errores                         : {len(errores)}",
    "-" * 55,
]

if copiados:
    lineas.append("\nARCHIVOS COPIADOS HOY:")
    for f in copiados:
        lineas.append(f"  + {f}")

if errores:
    lineas.append("\nERRORES:")
    for e in errores:
        lineas.append(f"  ! {e}")

lineas.append("\n" + "=" * 55)

# ── HISTORIAL DESCENDENTE ──────────────────────────────────────────────────────
if os.path.exists(REPORTE):
    with open(REPORTE, "r", encoding="utf-8") as fin:
        historial_anterior = fin.read()
else:
    historial_anterior = ""

with open(REPORTE, "w", encoding="utf-8") as fout:
    fout.write("\n".join(lineas) + "\n")
    if historial_anterior:
        fout.write("\n" + historial_anterior)

print("\n".join(lineas))

# ── ABRIR CARPETA DESTINO ──────────────────────────────────────────────────────
try:
    os.startfile(DESTINO)
except Exception:
    pass

input("\n  Presiona ENTER para cerrar...")