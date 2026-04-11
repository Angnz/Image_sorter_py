import shutil
from pathlib import Path
import rawpy
from PIL import Image

def process_cr3_directory(directory_path):
    # Convertimos la ruta a un objeto Path
    base_dir = Path(r"C:\Users\Ángel\Desktop\IMAGES SHOP")
    
    # Buscamos los archivos CR3
    cr3_files = list(base_dir.glob("*.[cC][rR]3"))
    
    if not cr3_files:
        print("No se encontraron archivos CR3 en la ruta especificada.")
        return

    print(f"Se encontraron {len(cr3_files)} archivos CR3. Iniciando proceso...\n")

    for cr3_path in cr3_files:
        file_name = cr3_path.stem
        target_dir = base_dir / file_name
        
        # 1. Crear la carpeta
        target_dir.mkdir(exist_ok=True)
        print(f"Procesando: {file_name} ...")
        
        new_cr3_path = target_dir / cr3_path.name
        
        # 2. COPIAR el archivo RAW (el original queda intacto en su lugar)
        if cr3_path.exists():
            # copy2 copia también los metadatos del sistema (fecha de creación, etc.)
            shutil.copy2(str(cr3_path), str(new_cr3_path))
        
        high_res_jpg_path = target_dir / f"{file_name}.jpg"
        ig_jpg_path = target_dir / f"{file_name}_Instagram.jpg"

        try:
            # Abrimos el RAW (rawpy solo lo lee, nunca lo modifica)
            with rawpy.imread(str(new_cr3_path)) as raw:
                # Revelamos el RAW a imagen
                rgb = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb)
                
                # 3. Guardar JPG de Alta Calidad (Poca compresión)
                img.save(high_res_jpg_path, 'JPEG', quality=95, optimize=True)
                
                # 4. Guardar JPG para Instagram (Mismas dimensiones, más liviano)
                img.save(ig_jpg_path, 'JPEG', quality=70, optimize=True)
                
            print(f"  ✓ Archivos RAW y JPGs listos en la carpeta '{file_name}'.")
            
            # 5. Comprimir la carpeta en un archivo ZIP
            zip_file_path = base_dir / file_name
            shutil.make_archive(str(zip_file_path), 'zip', str(target_dir))
            
            print(f"  ✓ Carpeta comprimida exitosamente en '{file_name}.zip'.")
            
        except Exception as e:
            print(f"  ✗ Error procesando {file_name}: {str(e)}")

# EJECUCIÓN
if __name__ == "__main__":
    # Sustituye esto por la ruta donde tienes tus fotos
    mi_ruta = r"E:\Bilder\2025\2025_11_Great_Britain" 
    
    process_cr3_directory(mi_ruta)