import cv2
import os
import requests
from cv2 import dnn_superres

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")
MODEL_PATH = os.path.join(BASE_DIR, "FSRCNN_x2.pb")

# Direct link to the Tiny AI Model (Fast & Sharp)
MODEL_URL = "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x2.pb"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("⬇️  Downloading AI Upscale Model (FSRCNN)...")
        r = requests.get(MODEL_URL)
        with open(MODEL_PATH, 'wb') as f:
            f.write(r.content)
        print("✅ Model Downloaded.")

def upscale_image():
    if not os.path.exists(NEWS_IMAGE):
        print("❌ No image to upscale.")
        return False

    print("🔬 THE LAB: Enhancing Image Quality...")
    
    # 1. Prepare the Neural Network
    download_model()
    
    try:
        sr = dnn_superres.DnnSuperResImpl_create()
        sr.readModel(MODEL_PATH)
        sr.setModel("fsrcnn", 2) # 2x Upscale (Magic Zoom)
        
        # 2. Load Image
        image = cv2.imread(NEWS_IMAGE)
        if image is None:
            print("❌ Failed to load image.")
            return False
            
        # 3. Enhance!
        upscaled = sr.upsample(image)
        
        # 4. Save Over Original
        cv2.imwrite(NEWS_IMAGE, upscaled)
        
        # Stats
        h, w, _ = image.shape
        new_h, new_w, _ = upscaled.shape
        print(f"✨ ENHANCED: {w}x{h} ➡️  {new_w}x{new_h} pixels")
        return True
        
    except Exception as e:
        print(f"⚠️ Upscale Failed (OpenCV Error): {e}")
        return False

if __name__ == "__main__":
    upscale_image()
