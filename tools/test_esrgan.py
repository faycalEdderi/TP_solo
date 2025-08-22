import os
from basicsr.archs.rrdbnet_arch import RRDBNet
import torch
from PIL import Image
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

models_dir = r"D:\IPSSI\Cours\Machine Learning\TP_solo\BasicSR\experiments\train_RealESRGANx4plus_400k_B12G4\models"
test_folder = r"D:\IPSSI\Cours\Machine Learning\TP_solo\dataset\low_res"
hr_folder = r"D:\IPSSI\Cours\Machine Learning\TP_solo\dataset\high_res"
output_base = r"D:\IPSSI\Cours\Machine Learning\TP_solo\results\test_outputs"

transform = lambda img: torch.from_numpy(np.array(img).transpose(2,0,1)).float().unsqueeze(0) / 255

def enhance_image(model, img_path):
    img = Image.open(img_path).convert('RGB')
    lr_tensor = transform(img)
    with torch.no_grad():
        sr_tensor = model(lr_tensor)
    sr_img = sr_tensor.squeeze().clamp(0,1).mul(255).byte().permute(1,2,0).cpu().numpy()
    return Image.fromarray(sr_img)

def evaluate(sr_img, hr_img):
    sr_np = np.array(sr_img)
    hr_np = np.array(hr_img)
    if min(sr_np.shape[0], sr_np.shape[1]) < 7 or min(hr_np.shape[0], hr_np.shape[1]) < 7:
        return None, None
    psnr = peak_signal_noise_ratio(hr_np, sr_np)
    ssim = structural_similarity(hr_np, sr_np, win_size=7, channel_axis=2)
    return psnr, ssim

summary = []
for ckpt in sorted(os.listdir(models_dir)):
    if ckpt.startswith('net_g_') and ckpt.endswith('.pth'):
        print(f"\nTest du modèle : {ckpt}")
        checkpoint_path = os.path.join(models_dir, ckpt)
        output_folder = os.path.join(output_base, ckpt.replace('.pth',''))
        os.makedirs(output_folder, exist_ok=True)
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
        ckpt = torch.load(checkpoint_path, map_location='cpu')
        if isinstance(ckpt, dict):
            if 'params_ema' in ckpt:
                model.load_state_dict(ckpt['params_ema'], strict=True)
            elif 'params' in ckpt:
                model.load_state_dict(ckpt['params'], strict=True)
            else:
                model.load_state_dict(ckpt, strict=True)
        else:
            model.load_state_dict(ckpt, strict=True)
        model.eval()
        psnr_list, ssim_list = [], []
        for img_name in os.listdir(test_folder):
            img_path = os.path.join(test_folder, img_name)
            sr_img = enhance_image(model, img_path)
            sr_img.save(os.path.join(output_folder, f"SR_{img_name}"))
            hr_img_path = os.path.join(hr_folder, img_name)
            if os.path.exists(hr_img_path):
                hr_img = Image.open(hr_img_path).convert('RGB')
                psnr, ssim = evaluate(sr_img, hr_img)
                if psnr is not None and ssim is not None:
                    psnr_list.append(psnr)
                    ssim_list.append(ssim)
        if psnr_list:
            avg_psnr = np.mean(psnr_list)
            avg_ssim = np.mean(ssim_list)
            print(f"Moyenne PSNR: {avg_psnr:.2f}, Moyenne SSIM: {avg_ssim:.4f}")
            summary.append((ckpt, avg_psnr, avg_ssim))
        else:
            print("Pas d'images HR pour calculer PSNR/SSIM.")

# print("\nRésumé des performances :")
# for ckpt, psnr, ssim in summary:
#     print(f"{ckpt}: PSNR={psnr:.2f}, SSIM={ssim:.4f}")
