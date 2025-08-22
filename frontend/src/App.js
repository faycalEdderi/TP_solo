
import React, { useState } from 'react';
import './App.css';


function App() {
  const [originalImage, setOriginalImage] = useState(null);
  const [upscaledImage, setUpscaledImage] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [zoomed, setZoomed] = useState(null); // 'original' | 'upscaled' | null

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setOriginalImage(e.target.files[0]);
      setUpscaledImage(null);
      setMetrics(null);
      setZoomed(null);
    }
  };

  const handleUpscale = async () => {
    if (!originalImage) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('image', originalImage);
    try {
      const response = await fetch('http://localhost:5000/upscale', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setUpscaledImage(data.upscaled_image); // base64 string
      setMetrics(data.metrics); // { psnr, ssim }
    } catch (error) {
      alert('Erreur lors du traitement.');
    }
    setLoading(false);
  };

  const handleZoom = (type) => {
    setZoomed(type === zoomed ? null : type);
  };

  return (
    <div className="sn-container">
      <h2 className="sn-title">Pixel Art Upscaler</h2>
      <input type="file" accept="image/*" onChange={handleImageChange} className="sn-input" />
      <button onClick={handleUpscale} disabled={!originalImage || loading} className="sn-btn">
        Upscaling
      </button>
      {loading && (
        <div className="sn-loader-container">
          <img src={process.env.PUBLIC_URL + '/8bit-mario-runing.gif'} alt="Mario loading" className="sn-loader-gif" />
          <div className="sn-loader-text">Traitement en cours...</div>
        </div>
      )}
      <div className="sn-images-row">
        {originalImage && (
          <div className="sn-image-block">
            <h4 className="sn-label">Image originale</h4>
            <img
              src={URL.createObjectURL(originalImage)}
              alt="original"
              className={`sn-img ${zoomed === 'original' ? 'sn-zoomed' : ''}`}
              onClick={() => handleZoom('original')}
            />
          </div>
        )}
        {upscaledImage && (
          <div className="sn-image-block">
            <h4 className="sn-label">Image upscalée</h4>
            <img
              src={`data:image/png;base64,${upscaledImage}`}
              alt="upscaled"
              className={`sn-img ${zoomed === 'upscaled' ? 'sn-zoomed' : ''}`}
              onClick={() => handleZoom('upscaled')}
            />
            {metrics && (
              <div className="sn-metrics">
                <span><strong>PSNR:</strong> {metrics.psnr.toFixed(2)}</span><br />
                <span><strong>SSIM:</strong> {metrics.ssim.toFixed(4)}</span>
              </div>
            )}
          </div>
        )}
      </div>
      {zoomed && (
        <div className="sn-modal" onClick={() => setZoomed(null)}>
          <img
            src={
              zoomed === 'original'
                ? URL.createObjectURL(originalImage)
                : `data:image/png;base64,${upscaledImage}`
            }
            alt={zoomed}
            className="sn-modal-img"
          />
        </div>
      )}
    </div>
  );
}

export default App;
