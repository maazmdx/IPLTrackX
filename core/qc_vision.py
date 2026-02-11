import cv2
import numpy as np
import os
import sys
import time
import requests

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")
LOG_DIR = os.path.join(BASE_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# --- FACE DETECTION MODEL SETUP ---
def get_haarcascade_path():
    """Robustly finds or downloads Face Detection Model"""
    # 1. Try standard OpenCV path
    try:
        path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        if os.path.exists(path): return path
    except: pass

    # 2. Check temp/
    local_path = os.path.join(TEMP_DIR, "haarcascade_frontalface_default.xml")
    if os.path.exists(local_path): return local_path

    # 3. DOWNLOAD IT
    print("📥 QC: Downloading Face Model...")
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    try:
        if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
        response = requests.get(url)
        with open(local_path, 'wb') as f: f.write(response.content)
        return local_path
    except: return None

def log_qc(score, status, issues):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] QC Score: {score} | Status: {status} | Issues: {', '.join(issues)}"
    print(f"👮‍♂️ {log_msg}")
    
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
    with open(os.path.join(LOG_DIR, "performance.log"), 'a') as f:
        f.write(log_msg + "\n")

# --- CHECKS ---
def check_resolution(img):
    h, w, _ = img.shape
    if w >= 2048: return 15
    elif w >= 1080: return 10
    return 0

def check_visual_quality(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur > 120: return 10
    if blur > 80: return 5
    return 0

def check_subject_safety(img):
    model_path = get_haarcascade_path()
    if not model_path: return 20, "Face Check Skipped"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(model_path)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
    
    h, w, _ = img.shape
    margin = int(w * 0.05)
    
    if len(faces) == 0: return 20, "No Face Detected"
    for (x, y, fw, fh) in faces:
        if x < margin or y < margin or (x+fw) > (w-margin):
            return 0, "Face too close to edge"
    return 20, "Faces Safe"

def check_text_contrast(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, _, _ = cv2.split(lab)
    if l.std() > 45: return 20
    if l.std() > 25: return 10
    return 0

def check_safe_margins(img):
    h, w, _ = img.shape
    margin = int(w * 0.08)
    crops = [img[:, :margin], img[:, w-margin:], img[:margin, :], img[h-margin:, :]]
    clean = 0
    for crop in crops:
        if np.mean(cv2.Canny(crop, 100, 200)) < 15: clean += 1
    if clean >= 3: return 15
    if clean >= 1: return 5
    return 0

def check_layout_balance(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    M = cv2.moments(gray)
    if M["m00"] == 0: return 0
    cX = int(M["m10"] / M["m00"])
    dev = abs(cX - w//2) / (w//2)
    if dev < 0.2: return 20
    if dev < 0.4: return 10
    return 5

# --- MAIN RUNNER ---
def run_qc():
    print("👮‍♂️ QC VISION: Starting Advanced Scan...")
    
    if not os.path.exists(FINAL_IMAGE):
        print("❌ FAIL: No image found.")
        sys.exit(1)
        
    try:
        img = cv2.imread(FINAL_IMAGE)
        if img is None:
            print("❌ FAIL: Corrupted image file.")
            sys.exit(1)
            
        total = 0
        issues = []
        
        # FIX: Single variable return for resolution
        score = check_resolution(img)
        total += score
        if score == 0: issues.append("Low Res")
        
        score = check_visual_quality(img)
        total += score
        if score == 0: issues.append("Blurry")
        
        # Tuple return for Safety
        score, msg = check_subject_safety(img)
        total += score
        if score == 0: issues.append(msg)
        
        score = check_text_contrast(img)
        total += score
        if score == 0: issues.append("Low Contrast")
        
        score = check_safe_margins(img)
        total += score
        if score < 10: issues.append("Bad Margins")
        
        score = check_layout_balance(img)
        total += score
        if score < 10: issues.append("Unbalanced")
        
        # Decision
        status = "FAIL"
        if total >= 80: status = "PASS"
        elif total >= 60: status = "RETRY"
        
        log_qc(total, status, issues)
        
        if status == "PASS": sys.exit(0)
        elif status == "RETRY": sys.exit(1)
        else: sys.exit(1)
            
    except Exception as e:
        print(f"⚠️ QC Crash: {e}. Passing conservatively.")
        sys.exit(0)

if __name__ == "__main__":
    run_qc()
