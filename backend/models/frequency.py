import io
from PIL import Image
import numpy as np
import cv2


def frequency_analysis(image_bytes: bytes) -> float:
    """
    Analyzes the frequency domain of the image using DCT + FFT.
    AI-generated images tend to have unnatural high-frequency patterns
    because generators don't perfectly replicate camera sensor noise.
    Returns a float 0-100 — higher = more suspicious frequency patterns.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("L")  # grayscale
        img_array = np.array(image, dtype=np.float32)

        h, w = img_array.shape

        # ── DCT Analysis ──────────────────────────────────────────────────────
        # Work on fixed-size tiles to normalize for image resolution.
        # Large images have naturally more high-freq energy — tiling removes that bias.
        tile_size = 512
        img_tile = cv2.resize(img_array, (tile_size, tile_size))
        dct = cv2.dct(img_tile)

        high_freq = dct[tile_size // 2:, tile_size // 2:]
        low_freq  = dct[:tile_size // 2, :tile_size // 2]

        high_energy = np.mean(np.abs(high_freq))
        low_energy  = np.mean(np.abs(low_freq)) + 1e-8

        hf_ratio = high_energy / low_energy

        # FIX: original multiplier of ×500 was way too aggressive — caused near-100%
        # scores even on clean real photos. ×150 gives more headroom (empirically safe).
        hf_score = min(hf_ratio * 150, 100)

        # ── FFT Analysis ──────────────────────────────────────────────────────
        fft = np.fft.fft2(img_array)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.log(np.abs(fft_shift) + 1)

        # AI images show periodic grid artifacts in FFT at regular intervals.
        center_h, center_w = h // 2, w // 2
        ring_mask = np.zeros_like(magnitude)
        for r in range(center_h - 5, center_h + 5):
            for c in range(center_w - 5, center_w + 5):
                if 0 <= r < h and 0 <= c < w:
                    ring_mask[r, c] = 1

        center_energy = np.mean(magnitude * ring_mask)
        total_energy  = np.mean(magnitude) + 1e-8
        fft_ratio = center_energy / total_energy

        fft_score = min(fft_ratio * 10, 100)

        # ── Combined score ────────────────────────────────────────────────────
        combined = hf_score * 0.6 + fft_score * 0.4
        return round(float(combined), 2)

    except Exception as e:
        print(f"[TruthLens] Frequency analysis error: {e}")
        return 50.0
