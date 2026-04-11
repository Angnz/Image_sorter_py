import shutil
import os
import subprocess
import json
from pathlib import Path
import rawpy
from PIL import Image

def get_exif_data(file_path):
    """Extrae metadatos usando ExifTool (solo lectura, no altera el archivo original)"""
    try:
        # Llama a exiftool pidiendo los datos en formato JSON (-j)
        cmd = ['exiftool', '-j', str("C:\Users\Ángel\Documents\GitHub\Image_sorter_py\exiftool-13.55_64\exiftool-13.55_64\exiftool.exe")]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parseamos el JSON para obtener un diccionario de Python
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
        print("\n  [!] ADVERTENCIA: No se encontró 'exiftool.exe' en la carpeta. Se usarán valores N/A.")
        return None
    except Exception as e:
        print(f"\n  [!] Error leyendo metadatos: {e}")
        return None

def process_cr3_directory(directory_path):
    base_dir = Path(r"C:\Users\Ángel\Desktop\IMAGES SHOP")  # Cambia esta ruta
    cr3_files = list(base_dir.glob("*.[cC][rR]3"))
    
    if not cr3_files:
        print("No se encontraron archivos CR3.")
        return

    print(f"Se encontraron {len(cr3_files)} archivos. Iniciando...\n")

    for cr3_path in cr3_files:
        file_name = cr3_path.stem
        target_dir = base_dir / file_name
        target_dir.mkdir(exist_ok=True)
        
        print(f"Procesando: {file_name} ...")
        
        # 1. Copiar el CR3 original (queda 100% intacto)
        new_cr3_path = target_dir / cr3_path.name
        if cr3_path.exists():
            shutil.copy2(str(cr3_path), str(new_cr3_path))
            
        # Calcular tamaño en MB
        cr3_size_mb = os.path.getsize(new_cr3_path) / (1024 * 1024)
        
        # 2. Obtener metadatos reales con ExifTool
        exif = get_exif_data(new_cr3_path)
        if not exif:
            # Valores por defecto si falla o falta el exiftool.exe
            exif = {k: 'N/A' for k in ['date_taken', 'camera_maker', 'camera_model', 'iso', 'f_stop', 'exposure', 'focal_length']}

        high_res_jpg_path = target_dir / f"{file_name}.jpg"
        ig_jpg_path = target_dir / f"{file_name}_Instagram.jpg"
        txt_path = target_dir / f"{file_name}_Info.txt"

        try:
            # 3. Procesar las imágenes (RAW a JPG)
            with rawpy.imread(str(new_cr3_path)) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb)
                width, height = img.size
                
                img.save(high_res_jpg_path, 'JPEG', quality=95, optimize=True)
                img.save(ig_jpg_path, 'JPEG', quality=70, optimize=True)
                
            # 4. Escribir el archivo TXT con la información correcta
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
                
            print(f"  ✓ Archivos, imágenes y TXT con metadatos creados con éxito.")
            
            # 5. Comprimir la carpeta a ZIP
            zip_file_path = base_dir / file_name
            shutil.make_archive(str(zip_file_path), 'zip', str(target_dir))
            print(f"  ✓ Carpeta comprimida en '{file_name}.zip'.\n")
            
        except Exception as e:
            print(f"  ✗ Error procesando la imagen {file_name}: {str(e)}\n")

if __name__ == "__main__":
    # Ruta de tus archivos
    mi_ruta = r"E:\Bilder\2025\2025_11_Great_Britain" 
    process_cr3_directory(mi_ruta)