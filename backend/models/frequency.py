import io
from PIL import Image
import numpy as np
import cv2

def frequency_analysis(image_bytes:bytes)->float:
    #Analyzes the frequency domain of the image using DCT.
    #AI-generated images tend to have unnatural high-frequency patterns
    #because generators don't perfectly replicate camera sensor noise.
    #Returns a float 0-100 — higher = more suspicious frequency patterns.


    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("L") #grayscale
        img_array = np.array(image,dtype=np.float32)

        #dct analysis

        dct = cv2.dct(img_array)

        #high freq energy ratio
        h,w = dct.shape
        high_freq = dct[h//2:,w//2:]
        low_freq = dct[:h//2,:w//2]

        high_energy = np.mean(np.abs(high_freq))
        low_energy = np.mean(np.abs(low_freq)) + 1e-8 #to avoid div by 0

        hf_ratio = high_energy/low_energy

        #FFT analysis

        fft = np.fft.fft2(img_array)
        fft_shift = np.fft.fftshift(fft)

        magnitude = np.log(np.abs(fft_shift)+1)


        #ai img often show grid artifacts in fft at periodic intervals

        center_h, center_w = h//2, w//2
        ring_mask = np.zeros_like(magnitude)
        for r in range(center_h-5,center_h+5):
            for c in range(center_w-5,center_w+5):
                if 0<=r <h and  0 <= c <w:
                    ring_mask[r,c] =1


        center_energy = np.mean(magnitude*ring_mask)
        total_energy = np.mean(magnitude) + 1e-8
        fft_ratio = center_energy/total_energy


        #combine signals into suspicion score
        #normalize 0-100 range (thresholds are empirical baselines)

        hf_score = min(hf_ratio*500,100)
        fft_score = min(fft_ratio*10,100)
        combined = (hf_score * 0.6 + fft_score*0.4)
        return round(float(combined),2)
    except Exception:
        print(f"Frequency analysis error: {e}")
        return 50.0



