from flask import Flask, request, jsonify
from flask_cors import CORS
import io
from PIL import Image
import base64
import torch
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

app = Flask(__name__)
CORS(app)

CHECKPOINT_PATH = r"D:/IPSSI/Cours/Machine Learning/TP_solo/BasicSR/experiments/train_RealESRGANx4plus_400k_B12G4/models/net_g_500.pth"

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
ckpt = torch.load(CHECKPOINT_PATH, map_location='cpu')
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

transform = lambda img: torch.from_numpy(np.array(img).transpose(2,0,1)).float().unsqueeze(0) / 255

def enhance_image(img):
    lr_tensor = transform(img)
    with torch.no_grad():
        sr_tensor = model(lr_tensor)
    sr_img = sr_tensor.squeeze().clamp(0,1).mul(255).byte().permute(1,2,0).cpu().numpy()
    return Image.fromarray(sr_img)

@app.route('/upscale', methods=['POST'])
def upscale():
    file = request.files['image']
    img = Image.open(file.stream).convert('RGB')
    # Redimensionne si trop grand (max 512x512)
    max_size = 512
    if img.width > max_size or img.height > max_size:
        ratio = min(max_size / img.width, max_size / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    sr_img = enhance_image(img)
    # Encode l'image upscalée en base64
    buffered = io.BytesIO()
    sr_img.save(buffered, format="PNG")
    upscaled_b64 = base64.b64encode(buffered.getvalue()).decode()
    # Calcul des métriques entre l'image d'entrée (redimensionnée) et l'image upscalée
    psnr, ssim = None, None
    try:
        lr_np = np.array(img)
        sr_np = np.array(sr_img)
        # Redimensionne lr_np à la taille de sr_np si besoin
        if lr_np.shape != sr_np.shape:
            lr_img_resized = Image.fromarray(lr_np).resize(sr_np.shape[1::-1], Image.LANCZOS)
            lr_np = np.array(lr_img_resized)
        if min(sr_np.shape[0], sr_np.shape[1]) >= 7 and min(lr_np.shape[0], lr_np.shape[1]) >= 7:
            psnr = float(peak_signal_noise_ratio(lr_np, sr_np))
            ssim = float(structural_similarity(lr_np, sr_np, win_size=7, channel_axis=2))
    except Exception:
        pass
    return jsonify({
        'upscaled_image': upscaled_b64,
        'metrics': {'psnr': psnr or 0, 'ssim': ssim or 0}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
