# main.py
import os
import kagglehub
from PIL import Image
from tqdm import tqdm

# === CONFIGURATION ===
DATASET_PATH = "ebrahimelgazar/pixel-art"
OUTPUT_LOW_RES = "dataset/low_res"
OUTPUT_HIGH_RES = "dataset/high_res"
SCALE_FACTOR = 4  # Ex: 128x128 → 32x32 (puis upscale vers 128x128)
MAX_IMAGES = 30    # Nombre d'images à traiter

# Créer les dossiers
os.makedirs(OUTPUT_LOW_RES, exist_ok=True)
os.makedirs(OUTPUT_HIGH_RES, exist_ok=True)

def download_dataset():
    print("🔽 Téléchargement du dataset via kagglehub...")
    try:
        path = kagglehub.dataset_download(DATASET_PATH)
        print(f"✅ Dataset téléchargé à : {path}")
        return path
    except Exception as e:
        print(f"❌ Erreur de téléchargement : {e}")
        return None

def build_low_high_pairs(dataset_path):
    print("🔄 Création des paires low-res → high-res...")
    count = 0

    # Parcours tous les fichiers PNG
    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")) and count < MAX_IMAGES:
                try:
                    img_path = os.path.join(root, file)
                    img = Image.open(img_path).convert("RGB")

                    # On garde seulement les images > 32x32
                    if img.width < 32 or img.height < 32:
                        continue

                    # Génère une version pixelisée
                    low_size = (img.width // SCALE_FACTOR, img.height // SCALE_FACTOR)
                    high_size = (img.width, img.height)

                    low_img = img.resize(low_size, Image.NEAREST)
                    # Optionnel : on peut aussi forcer à une taille fixe (ex: 64x64)
                    # low_img = low_img.resize((64, 64), Image.NEAREST) si besoin

                    # Nom unique
                    safe_name = f"img_{count:03d}.png"

                    # Sauvegarde
                    low_img.save(os.path.join(OUTPUT_LOW_RES, safe_name))
                    img.save(os.path.join(OUTPUT_HIGH_RES, safe_name))

                    count += 1
                    tqdm.write(f"✅ {safe_name}: {low_size} → {high_size}")

                except Exception as e:
                    print(f"❌ Erreur avec {file}: {e}")

    print(f"\n🎉 Dataset généré : {count} paires dans {OUTPUT_LOW_RES} et {OUTPUT_HIGH_RES}")

if __name__ == "__main__":
    # 1. Télécharger
    dataset_path = download_dataset()
    if not dataset_path:
        exit(1)

    # 2. Générer les paires
    build_low_high_pairs(dataset_path)

    # 3. Afficher un exemple (optionnel)
    example_low = os.path.join(OUTPUT_LOW_RES, os.listdir(OUTPUT_LOW_RES)[0])
    example_high = os.path.join(OUTPUT_HIGH_RES, os.listdir(OUTPUT_HIGH_RES)[0])

    print(f"\n📁 Exemples :")
    print(f"   Low-res : {example_low}")
    print(f"   High-res: {example_high}")