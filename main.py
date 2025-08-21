# main.py
import os
from PIL import Image

# === CONFIGURATION ===
INPUT_HIGH_RES = "dataset/high_res"
OUTPUT_LOW_RES = "dataset/low_res"
SCALE_FACTOR = 4  # 4x downscaling (ex: 64x64 → 16x16)
MAX_IMAGES = 30    # Limite pour aller vite

# Créer les dossiers
os.makedirs(OUTPUT_LOW_RES, exist_ok=True)
os.makedirs(INPUT_HIGH_RES, exist_ok=True)

def build_low_high_pairs():
    """
    Parcourt le dossier high_res et génère des paires low-res / high-res
    Les images haute résolution doivent être placées dans dataset/high_res/
    Les versions pixelisées seront générées dans dataset/low_res/
    """
    print("🔄 Création des paires low-res → high-res...")
    print(f"🔍 Recherche d'images dans : {INPUT_HIGH_RES}")

    # Liste tous les fichiers image
    found_files = []
    for root, _, files in os.walk(INPUT_HIGH_RES):
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
                safe_name = os.path.basename(img_path)

                # Sauvegarder
                low_img.save(os.path.join(OUTPUT_LOW_RES, safe_name), "PNG")
                img.save(os.path.join(INPUT_HIGH_RES, safe_name), "PNG")

                count += 1
                print(f"✅ {safe_name}: {low_size} → {img.size}")

        except Exception as e:
            # Affiche le type d'erreur pour mieux déboguer
            print(f"❌ [{type(e).__name__}] Échec avec : {img_path}")
            print(f"   → {e}")

    print(f"\n🎉 Dataset généré : {count} paires sauvegardées.")

if __name__ == "__main__":
    # Générer les paires à partir des images placées dans high_res
    build_low_high_pairs()

    # Afficher un exemple (uniquement si des images existent)
    low_files = os.listdir(OUTPUT_LOW_RES)
    high_files = os.listdir(INPUT_HIGH_RES)

    if low_files and high_files:
        example_low = os.path.join(OUTPUT_LOW_RES, low_files[0])
        example_high = os.path.join(INPUT_HIGH_RES, high_files[0])
        print(f"\n📁 Exemples générés :")
        print(f"   Low-res : {example_low} ({Image.open(example_low).size})")
        print(f"   High-res: {example_high} ({Image.open(example_high).size})")
    else:
        print("\n❌ Aucune image générée. Vérifie les erreurs ci-dessus.")