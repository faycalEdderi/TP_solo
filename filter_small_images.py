import os
from PIL import Image

# Dossiers à vérifier
HR_DIR = 'BasicSR/datasets/gaming/HR'
LR_DIR = 'BasicSR/datasets/gaming/LR'
SCALE = 4
MIN_LR_SIZE = 64  # patch size minimum pour LR
MIN_HR_SIZE = MIN_LR_SIZE * SCALE

# Fonction pour supprimer les images trop petites
def filter_images(folder, min_size):
    removed = []
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        try:
            with Image.open(path) as img:
                w, h = img.size
                if w < min_size or h < min_size:
                    os.remove(path)
                    removed.append(fname)
        except Exception as e:
            print(f"Erreur avec {fname}: {e}")
    return removed

removed_hr = filter_images(HR_DIR, MIN_HR_SIZE)
removed_lr = filter_images(LR_DIR, MIN_LR_SIZE)

print(f"Images HR supprimées: {removed_hr}")
print(f"Images LR supprimées: {removed_lr}")
print("Filtrage terminé.")
