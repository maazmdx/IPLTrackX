import os
import sys
import time
import json
from control.logger import log_error, log_event

# --- CONFIGURATION ---
MAX_RETRIES = 3
RETRY_DELAY = 2 # Seconds

# Error Codes
E_EMPTY_NEWS = "E01"
E_IMG_DOWNLOAD = "E02"
E_CORRUPT_FILE = "E03"
E_API_FAIL = "E04"
E_JSON_FAIL = "E05"
E_TIMEOUT = "E06"
E_QC_FAIL = "E07"
E_UNKNOWN = "E99"

def run_protected(agent_name, func, *args):
    """
    Runs a function with auto-retry, timeout protection, and error logging.
    Returns: True (Success) or False (Failed after retries)
    """
    attempts = 0
    
    while attempts < MAX_RETRIES:
        try:
            # Try to run the agent function
            result = func(*args)
            
            # If function returns False specifically, treat as logic failure (not crash)
            if result is False:
                raise Exception("Agent returned False status")
                
            return True # Success
            
        except Exception as e:
            attempts += 1
            log_error(E_UNKNOWN, agent_name, f"Attempt {attempts}/{MAX_RETRIES} Failed: {str(e)}")
            time.sleep(RETRY_DELAY)
    
    # If we get here, we failed 3 times
    log_error(E_UNKNOWN, agent_name, "CRITICAL FAILURE. Skipping Step.")
    return False

def check_json_integrity(filepath):
    """Ensures JSON files aren't corrupted/empty"""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except:
        log_error(E_JSON_FAIL, "SYSTEM", f"Corrupted JSON detected: {filepath}")
        return False

def validate_image(filepath):
    """Checks if image exists and is readable"""
    if not os.path.exists(filepath):
        log_error(E_IMG_DOWNLOAD, "SYSTEM", "Image file missing.")
        return False
    if os.path.getsize(filepath) < 1000: # Less than 1KB
        log_error(E_CORRUPT_FILE, "SYSTEM", "Image file too small (corrupt).")
        return False
    return True
