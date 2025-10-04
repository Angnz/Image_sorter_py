import os
from PIL import Image

# =============================
# CONFIGURACIÓN - EDITA AQUÍ 
# =============================
INPUT_FOLDER = "C:\\Users\\Ángel\\Pictures\\00_Mano Ievute\\Vinted_2\\IEVITA\\Neuer Ordner"      # Carpeta donde están las imágenes
SIZE_LIMIT_MB = 9          # Límite en MB
REDUCE_PERCENT = 25          # Porcentaje de reducción
# =============================


def resize_images_bulk(input_folder, size_limit_mb=2, reduce_percent=25):
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)

        # Solo procesar archivos que sean imágenes
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
            continue
        
        # Revisar tamaño del archivo
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        if file_size_mb <= size_limit_mb:
            print(f" {filename} ({file_size_mb:.2f} MB) → No necesita reducción.")
            continue

        # Crear nuevo nombre con sufijo _resized
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_resized{ext}"
        output_path = os.path.join(input_folder, output_filename)

        # Abrir imagen
        with Image.open(input_path) as img:
            # Calcular nuevo tamaño
            new_width = int(img.width * (100 - reduce_percent) / 100)
            new_height = int(img.height * (100 - reduce_percent) / 100)
            resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)

            # Guardar en la misma carpeta con nuevo nombre
            resized_img.save(output_path, optimize=True, quality=85)

        print(f"{filename} ({file_size_mb:.2f} MB) → Guardada como {output_filename}")

if __name__ == "__main__":
    resize_images_bulk(INPUT_FOLDER, SIZE_LIMIT_MB, REDUCE_PERCENT)
    print("🎉 Proceso completado.")

