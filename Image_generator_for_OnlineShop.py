import shutil
import os
import subprocess
import json
from pathlib import Path
import rawpy
from PIL import Image
from tqdm import tqdm

# ================= CONFIGURACIÓN DINÁMICA =================
# Detecta automáticamente la carpeta del usuario actual (ej: C:\Users\Ángel)
USER_HOME = Path.home()

# Construye la ruta de ExifTool de forma segura usando el home del usuario
EXIFTOOL_EXE = str(USER_HOME / "Documents" / "GitHub" / "Image_sorter_py" / "exiftool-13.55_64" / "exiftool-13.55_64" / "exiftool.exe")
# ==========================================================

def get_exif_data(file_path):
    """Extrae metadatos usando ExifTool ejecutándolo desde la propia carpeta de la imagen"""
    try:
        # 1. Separamos la ruta: la carpeta por un lado, y el nombre del archivo por otro
        file_obj = Path(file_path)
        folder_dir = str(file_obj.parent)
        filename = file_obj.name
        
        # 2. Le decimos a ExifTool que lea solo el "nombre.CR3", sin toda la ruta
        cmd = [EXIFTOOL_EXE, '-charset', 'filename=UTF8', '-j', filename]
        
        # 3. cwd=folder_dir: Esto abre un terminal "invisible" directamente dentro de la carpeta de la foto
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=folder_dir)
        
        # Si sigue vacío por alguna razón, lanzamos una excepción clara
        if not result.stdout.strip():
            raise ValueError(f"ExifTool no devolvió datos para {filename}")
            
        metadata = json.loads(result.stdout)[0]
        
        return {
            'date_taken': metadata.get('DateTimeOriginal', 'N/A'),
            'camera_maker': metadata.get('Make', 'N/A'),
            'camera_model': metadata.get('Model', 'N/A'),
            'iso': metadata.get('ISO', 'N/A'),
            'f_stop': f"f/{metadata.get('FNumber')}" if metadata.get('FNumber') else 'N/A',
            'exposure': f"{metadata.get('ExposureTime')} sec" if metadata.get('ExposureTime') else 'N/A',
            'focal_length': f"{metadata.get('FocalLength')} mm" if metadata.get('FocalLength') else 'N/A'
        }
    except FileNotFoundError:
        print("\n  [!] ADVERTENCIA: No se encontró 'exiftool.exe' en la ruta especificada.")
        return None
    except Exception as e:
        # Usamos tqdm.write para que el error no rompa la barra de progreso visual
        tqdm.write(f"\n  [!] Error leyendo metadatos: {e}")
        if 'result' in locals() and hasattr(result, 'stderr') and result.stderr:
            tqdm.write(f"      Error interno de ExifTool: {result.stderr.strip()}")
        return None

def process_cr3_directory(directory_path):
    base_dir = Path(directory_path)
    cr3_files = list(base_dir.glob("*.[cC][rR]3"))
    
    if not cr3_files:
        print("No se encontraron archivos CR3.")
        return

    print(f"\n📷 Se encontraron {len(cr3_files)} archivos CR3. Iniciando proceso...\n")

    for cr3_path in tqdm(cr3_files, desc="Procesando imágenes", unit="foto"):
        file_name = cr3_path.stem
        target_dir = base_dir / file_name
        target_dir.mkdir(exist_ok=True)
        
        new_cr3_path = target_dir / cr3_path.name
        
        try:
            # 1. Copiar el CR3 original
            if cr3_path.exists():
                shutil.copy2(str(cr3_path), str(new_cr3_path))
                
            cr3_size_mb = os.path.getsize(new_cr3_path) / (1024 * 1024)
            
            # 2. Extraer metadatos con ExifTool
            exif = get_exif_data(new_cr3_path)
            if not exif:
                exif = {k: 'N/A' for k in ['date_taken', 'camera_maker', 'camera_model', 'iso', 'f_stop', 'exposure', 'focal_length']}

            high_res_jpg_path = target_dir / f"{file_name}.jpg"
            ig_jpg_path = target_dir / f"{file_name}_Instagram.jpg"
            txt_path = target_dir / f"{file_name}_Info.txt"

            # 3. Revelar RAW y crear JPGs
            with rawpy.imread(str(new_cr3_path)) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb)
                width, height = img.size
                
                img.save(high_res_jpg_path, 'JPEG', quality=95, optimize=True)
                img.save(ig_jpg_path, 'JPEG', quality=70, optimize=True)
                
            # 4. Crear el archivo TXT de información
            txt_content = f"""-----------------------------------------------------
What’s included in your download:
1 x CR3 File (RAW): Original uncompressed file [{cr3_size_mb:.1f} MB] for professional editing and maximum flexibility.
1 x High-Res JPG: Full-size image [{width} x {height} px] ready for large-format printing or personal use.
1 x JPG_Instagram: File Size Optimized perfectly for your social media feed.

Author: Spotedfy

CR3 File Details:
RAW (.CR3)
Type: CR3 File
Size: {cr3_size_mb:.1f} MB
Date taken: {exif['date_taken']}
Dimensions: {width} x {height}
Camera maker: {exif['camera_maker']}
Camera model: {exif['camera_model']}
ISO speed: {exif['iso']}
F-stop: {exif['f_stop']}
Exposure time: {exif['exposure']}
Focal length: {exif['focal_length']}
-----------------------------------------------------"""
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(txt_content)
                
            # 5. Comprimir la carpeta en un ZIP (dejando la carpeta intacta)
            zip_file_path = base_dir / file_name
            shutil.make_archive(str(zip_file_path), 'zip', str(target_dir))
            
        except Exception as e:
            tqdm.write(f"\n ✗ Error procesando {file_name}: {str(e)}")

    print("\n✅ ¡Proceso completado con éxito!")

# EJECUCIÓN
if __name__ == "__main__":
    # Construye dinámicamente: C:\Users\Ángel\Desktop\IMAGES SHOP
    mi_ruta = str(USER_HOME / "Desktop" / "IMAGES SHOP")
    
    process_cr3_directory(mi_ruta)