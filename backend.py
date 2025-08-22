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
    sr_img = enhance_image(img)
    # Encode l'image upscalée en base64
    buffered = io.BytesIO()
    sr_img.save(buffered, format="PNG")
    upscaled_b64 = base64.b64encode(buffered.getvalue()).decode()
    # Calcul des métriques si HR disponible
    psnr, ssim = None, None
    try:
        hr_img = img  # Si tu veux comparer à l'original (à adapter si tu as une vraie HR)
        sr_np = np.array(sr_img)
        hr_np = np.array(hr_img)
        if min(sr_np.shape[0], sr_np.shape[1]) >= 7 and min(hr_np.shape[0], hr_np.shape[1]) >= 7:
            psnr = float(peak_signal_noise_ratio(hr_np, sr_np))
            ssim = float(structural_similarity(hr_np, sr_np, win_size=7, channel_axis=2))
    except Exception:
        pass
    return jsonify({
        'upscaled_image': upscaled_b64,
        'metrics': {'psnr': psnr or 0, 'ssim': ssim or 0}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
