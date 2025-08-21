import os
from PIL import Image

INPUT_HIGH_RES = "dataset/high_res"
OUTPUT_LOW_RES = "dataset/low_res"
SCALE_FACTOR = 4  # 4x downscaling (ex: 64x64 → 16x16)
MAX_IMAGES = 30    # Limite pour aller vite

# Création des dossiers si nécessaire
os.makedirs(OUTPUT_LOW_RES, exist_ok=True)
os.makedirs(INPUT_HIGH_RES, exist_ok=True)

def build_low_high_pairs():
    """
    Parcourt le dossier high_res et génère des paires low-res / high-res
    Les images haute résolution doivent être placées dans dataset/high_res/
    Les versions pixelisées seront générées dans dataset/low_res/
    """
    print("Création des paires low-res → high-res...")
    print(f"🔍 Recherche d'images dans : {INPUT_HIGH_RES}")

    found_files = []
    for root, _, files in os.walk(INPUT_HIGH_RES):
        for file in files:
            ext = file.lower().split(".")[-1]
            if ext in ["png", "jpg", "jpeg", "bmp", "tiff"]:
                found_files.append(os.path.join(root, file))

    print(f" {len(found_files)} images trouvées au total.")
    if found_files:
        print("Exemples :")
        for f in found_files[:3]:
            print(f"   - {f}")

    # Traitement des images
    count = 0
    for img_path in found_files:
        if count >= MAX_IMAGES:
            print(f"Limite de {MAX_IMAGES} images atteinte.")
            break

        try:
            with Image.open(img_path) as img:
                if img.mode not in ["RGB", "RGBA"]:
                    img = img.convert("RGB")

                # Redimensionner si trop grande
                if img.width > 512 or img.height > 512:
                    ratio = min(512 / img.width, 512 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)

                if img.width < 16 or img.height < 16:
                    continue

                # Calculer la taille HR pour qu'elle soit bien un multiple de SCALE_FACTOR
                hr_width = (img.width // SCALE_FACTOR) * SCALE_FACTOR
                hr_height = (img.height // SCALE_FACTOR) * SCALE_FACTOR
                img_hr = img.resize((hr_width, hr_height), Image.LANCZOS)

                # Générer low-res
                low_size = (hr_width // SCALE_FACTOR, hr_height // SCALE_FACTOR)
                low_img = img_hr.resize(low_size, Image.NEAREST)

                safe_name = os.path.basename(img_path)

                low_img.save(os.path.join(OUTPUT_LOW_RES, safe_name), "PNG")
                img_hr.save(os.path.join(INPUT_HIGH_RES, safe_name), "PNG")

                count += 1
                print(f"{safe_name}: {low_size} → {img_hr.size}")

        except Exception as e:
            print(f"[{type(e).__name__}] Échec avec : {img_path}")
            print(f"   → {e}")

    print(f"\nDataset généré : {count} paires sauvegardées.")

if __name__ == "__main__":
    # Générer les paires à partir des images placées dans high_res
    build_low_high_pairs()

    # Afficher un exemple
    low_files = os.listdir(OUTPUT_LOW_RES)
    high_files = os.listdir(INPUT_HIGH_RES)

    if low_files and high_files:
        example_low = os.path.join(OUTPUT_LOW_RES, low_files[0])
        example_high = os.path.join(INPUT_HIGH_RES, high_files[0])
        print(f"\nExemples générés :")
        print(f"   Low-res : {example_low} ({Image.open(example_low).size})")
        print(f"   High-res: {example_high} ({Image.open(example_high).size})")
    else:
        print("\n ERROR :Aucune image générée. Vérifie les erreurs ci-dessus.")