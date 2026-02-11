import logging
import os
import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# File Paths
SYSTEM_LOG = os.path.join(LOG_DIR, "system.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")
PERF_LOG = os.path.join(LOG_DIR, "performance.log")

# --- SETUP LOGGERS ---
def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

sys_logger = setup_logger('system', SYSTEM_LOG)
err_logger = setup_logger('error', ERROR_LOG)
perf_logger = setup_logger('performance', PERF_LOG)

# --- PUBLIC FUNCTIONS ---

def log_event(agent, message):
    """Logs general system activity"""
    print(f"🔹 [{agent}] {message}")
    sys_logger.info(f"[{agent}] {message}")

def log_error(code, agent, message):
    """Logs failures and critical errors"""
    print(f"❌ [{agent}] ERROR {code}: {message}")
    err_logger.error(f"[{agent}] Code: {code} - {message}")

def log_performance(agent, metric, value):
    """Logs stats like execution time or QC score"""
    msg = f"[{agent}] {metric}: {value}"
    # print(f"📊 {msg}") # Optional: Don't print to console to keep it clean
    perf_logger.info(msg)

def log_qc(score, status, issues):
    """Logs Quality Control results"""
    msg = f"QC Score: {score} | Status: {status} | Issues: {issues}"
    print(f"👮‍♂️ {msg}")
    perf_logger.info(f"[QC_VISION] {msg}")

def log_upload(filename, status):
    """Logs final upload status"""
    msg = f"Upload: {status} -> {filename}"
    sys_logger.info(f"[PUBLISHER] {msg}")
    if status == "SUCCESS":
        print(f"✨ {msg}")
    else:
        print(f"⚠️ {msg}")
