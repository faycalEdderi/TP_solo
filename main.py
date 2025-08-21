# main.py
import os
import kagglehub
from PIL import Image
from tqdm import tqdm

# === CONFIGURATION ===
DATASET_PATH = "ebrahimelgazar/pixel-art"
OUTPUT_LOW_RES = "dataset/low_res"
OUTPUT_HIGH_RES = "dataset/high_res"
SCALE_FACTOR = 4  # 4x upscaling (ex: 16x16 → 64x64)
MAX_IMAGES = 30    # Limite pour aller vite

# Créer les dossiers
os.makedirs(OUTPUT_LOW_RES, exist_ok=True)
os.makedirs(OUTPUT_HIGH_RES, exist_ok=True)

def download_dataset():
    """Télécharge le dataset via kagglehub"""
    print("🔽 Téléchargement du dataset via kagglehub...")
    try:
        path = kagglehub.dataset_download(DATASET_PATH)
        print(f"✅ Dataset téléchargé à : {path}")
        return path
    except Exception as e:
        print(f"❌ Erreur de téléchargement : {type(e).__name__} – {e}")
        return None

def build_low_high_pairs(dataset_path):
    """Parcourt le dataset et génère des paires low-res / high-res"""
    print("🔄 Création des paires low-res → high-res...")
    print(f"🔍 Recherche d'images dans : {dataset_path}")

    # Liste tous les fichiers image
    found_files = []
    for root, _, files in os.walk(dataset_path):
        for file in files:
            ext = file.lower().split(".")[-1]
            if ext in ["png", "jpg", "jpeg", "bmp", "tiff"]:
                found_files.append(os.path.join(root, file))

    print(f"📁 {len(found_files)} images trouvées au total.")
    if found_files:
        print("📄 Exemples :")
        for f in found_files[:3]:
            print(f"   - {f}")

    # Traitement des images
    count = 0
    for img_path in found_files:
        if count >= MAX_IMAGES:
            print(f"📌 Limite de {MAX_IMAGES} images atteinte.")
            break

        try:
            # Ouvrir l'image
            with Image.open(img_path) as img:
                # Convertir en RGB (évite problèmes de mode P, LA, etc.)
                if img.mode not in ["RGB", "RGBA"]:
                    img = img.convert("RGB")

                # Redimensionner si trop grande (optionnel)
                if img.width > 512 or img.height > 512:
                    ratio = min(512 / img.width, 512 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)

                # Vérifier taille min
                if img.width < 16 or img.height < 16:
                    continue

                # Générer low-res
                low_size = (img.width // SCALE_FACTOR, img.height // SCALE_FACTOR)
                if low_size[0] == 0 or low_size[1] == 0:
                    continue

                low_img = img.resize(low_size, Image.NEAREST)

                # Nommer
                safe_name = f"img_{count:03d}.png"

                # Sauvegarder
                low_img.save(os.path.join(OUTPUT_LOW_RES, safe_name), "PNG")
                img.save(os.path.join(OUTPUT_HIGH_RES, safe_name), "PNG")

                count += 1
                print(f"✅ {safe_name}: {low_size} → {img.size}")

        except Exception as e:
            # Affiche le type d'erreur pour mieux déboguer
            print(f"❌ [{type(e).__name__}] Échec avec : {img_path}")
            print(f"   → {e}")

    print(f"\n🎉 Dataset généré : {count} paires sauvegardées.")

if __name__ == "__main__":
    # 1. Télécharger le dataset
    dataset_path = download_dataset()
    if not dataset_path:
        print("❌ Impossible de télécharger le dataset.")
        exit(1)

    # 2. Générer les paires
    build_low_high_pairs(dataset_path)

    # 3. Afficher un exemple (uniquement si des images existent)
    low_files = os.listdir(OUTPUT_LOW_RES)
    high_files = os.listdir(OUTPUT_HIGH_RES)

    if low_files and high_files:
        example_low = os.path.join(OUTPUT_LOW_RES, low_files[0])
        example_high = os.path.join(OUTPUT_HIGH_RES, high_files[0])
        print(f"\n📁 Exemples générés :")
        print(f"   Low-res : {example_low} ({Image.open(example_low).size})")
        print(f"   High-res: {example_high} ({Image.open(example_high).size})")
    else:
        print("\n❌ Aucune image générée. Vérifie les erreurs ci-dessus.")