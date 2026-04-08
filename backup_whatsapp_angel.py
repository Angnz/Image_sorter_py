import os
import shutil
from datetime import datetime


# ── RUTAS ──────────────────────────────────────────────────────────────────────
FUENTES = [
    r"C:\Users\Ángel\Pictures\Whatsapp_S9\Videos",
    r"C:\Users\Ángel\Pictures\Whatsapp_S9\Fotos",
]
DESTINO = r"E:\Bilder\Whatsapp_backup"
REPORTE = r"E:\Bilder\Whatsapp_backup\backup_whatsapp_reporte_{mes_ano}.txt"


# ── CREAR DESTINO SI NO EXISTE ─────────────────────────────────────────────────
os.makedirs(DESTINO, exist_ok=True)


# ── COPIA RECURSIVA (sin sobreescribir ni borrar) ──────────────────────────────-
copiados    = []
omitidos    = []
errores     = []
inicio      = datetime.now()
fecha_hoy   = inicio.strftime("%d/%m/%Y")
hora_inicio = inicio.strftime("%H:%M:%S")
mes_ano     = inicio.strftime("%Y_%m")

#crear reporte y save path con variable definida
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
            origen  = os.path.join(raiz, archivo)
            destino = os.path.join(carpeta_destino, archivo)
            ruta_log = os.path.join(nombre_subcarpeta, ruta_relativa, archivo)

            if os.path.exists(destino):
                omitidos.append(ruta_log)
            else:
                try:
                    shutil.copy2(origen, destino)
                    copiados.append(ruta_log)
                except Exception as e:
                    errores.append(f"{ruta_log}: {e}")


# ── REPORTE ────────────────────────────────────────────────────────────────────
fin      = datetime.now()
hora_fin = fin.strftime("%H:%M:%S")

# ✅ NUEVO: duración total en segundos
duracion = int((fin - inicio).total_seconds())

lineas = [
    "=" * 55,
    f"  BACKUP WHATSAPP — {fecha_hoy}",
    "=" * 55,
    f"  Inicio : {hora_inicio}   |   Fin: {hora_fin}",
    f"  ⏱️  Duración total                  : {duracion} segundos",  # ✅ NUEVO
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


#----------------------------------
#Para el reporte

#crear reporte sovreescribiendo el anterior
#with open(REPORTE, "w", encoding="utf-8") as fout:   # ← "a" para acumular historial
#    fout.write("\n".join(lineas) + "\n")
#-------------------------------------


# crear reporte acumulando historial desendiente (lo nuevo arriba)
# Leer historial anterior (si existe)

if os.path.exists(REPORTE):
    with open(REPORTE, "r", encoding="utf-8") as fin:
        historial_anterior = fin.read()
else:
    historial_anterior = ""

# Escribir: nuevo reporte arriba + historial abajo
with open(REPORTE, "w", encoding="utf-8") as fout:
    fout.write("\n".join(lineas) + "\n")
    if historial_anterior:
        fout.write("\n" + historial_anterior)

#---------------------------------    

print("\n".join(lineas))


# ── ABRIR CARPETA DESTINO ──────────────────────────────────────────────────────
try:
    os.startfile(DESTINO)
except Exception:
    pass


# ✅ NUEVO: mantiene la ventana CMD abierta hasta que el usuario presione ENTER
input("\n  Presiona ENTER para cerrar...")