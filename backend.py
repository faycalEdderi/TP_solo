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
    # Génère deux graphiques séparés (PSNR et SSIM)
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    # Graphique PSNR
    fig_psnr, ax_psnr = plt.subplots()
    ax_psnr.bar(['PSNR'], [psnr or 0], color='skyblue')
    ax_psnr.set_ylim(0, max(50, (psnr or 0) + 5))
    ax_psnr.set_title('PSNR')
    plt.tight_layout()
    buf_psnr = io.BytesIO()
    plt.savefig(buf_psnr, format='png')
    buf_psnr.seek(0)
    psnr_graph_b64 = base64.b64encode(buf_psnr.read()).decode('utf-8')
    plt.close(fig_psnr)
    # Graphique SSIM
    fig_ssim, ax_ssim = plt.subplots()
    ax_ssim.bar(['SSIM'], [ssim or 0], color='orange')
    ax_ssim.set_ylim(0, 1)
    ax_ssim.set_title('SSIM')
    plt.tight_layout()
    buf_ssim = io.BytesIO()
    plt.savefig(buf_ssim, format='png')
    buf_ssim.seek(0)
    ssim_graph_b64 = base64.b64encode(buf_ssim.read()).decode('utf-8')
    plt.close(fig_ssim)
    psnr_graph_url = f"data:image/png;base64,{psnr_graph_b64}"
    ssim_graph_url = f"data:image/png;base64,{ssim_graph_b64}"
    return jsonify({
        'upscaled_image': upscaled_b64,
        'metrics': {'psnr': psnr or 0, 'ssim': ssim or 0},
        'psnr_graph': psnr_graph_url,
        'ssim_graph': ssim_graph_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
