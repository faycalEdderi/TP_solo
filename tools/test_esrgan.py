import os
from basicsr.archs.rrdbnet_arch import RRDBNet
import torch
from PIL import Image
import numpy as np

# Chemins à adapter
checkpoint_path = r"D:\IPSSI\Cours\Machine Learning\TP_solo\BasicSR\experiments\train_RealESRGANx4plus_400k_B12G4\models\net_g_500.pth"
test_folder = r"D:\IPSSI\Cours\Machine Learning\TP_solo\datasets\gaming\test\LR"
output_folder = r"D:\IPSSI\Cours\Machine Learning\TP_solo\results\test_outputs"
os.makedirs(output_folder, exist_ok=True)

# Charger le modèle
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'), strict=True)
model.eval()

# Fonction de prétraitement
transform = lambda img: torch.from_numpy(np.array(img).transpose(2,0,1)).float().unsqueeze(0) / 255

def enhance_image(img_path):
    img = Image.open(img_path).convert('RGB')
    lr_tensor = transform(img)
    with torch.no_grad():
        sr_tensor = model(lr_tensor)
    sr_img = sr_tensor.squeeze().clamp(0,1).mul(255).byte().permute(1,2,0).cpu().numpy()
    return Image.fromarray(sr_img)

# Traitement des images du dossier test
for img_name in os.listdir(test_folder):
    img_path = os.path.join(test_folder, img_name)
    sr_img = enhance_image(img_path)
    sr_img.save(os.path.join(output_folder, f"SR_{img_name}"))
    print(f"Image traitée : {img_name}")

print("Test terminé. Les images améliorées sont dans :", output_folder)
