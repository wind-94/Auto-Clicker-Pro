import os
import shutil
import sys
import json
from cryptography.fernet import Fernet

def _find_tesseract():
    """Smartly searches the user's system for the Tesseract OCR executable."""
    # 1. Check if Tesseract is registered in the Windows Environmental Variables
    system_path = shutil.which("tesseract")
    if system_path:
        return system_path
    
    # 2. If not found, check the default installation path
    common_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path
        
    # Return empty if cpmpletely missing
    return ""


# --- CONFIGURATION ---
TESSERACT_PATH = _find_tesseract()
OCR_CONFIG  = "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"

# Determine base directory whether running as script or .exe
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths for the encrypted data and the hidden key
CONFIG_PATH = os.path.join(BASE_DIR, "bot_config.enc")
KEY_PATH = os.path.join(BASE_DIR, ".secret_key")
ICON_PATH = os.path.join(BASE_DIR, "logo.ico")

def _get_cipher():
    """Retrieves or generates the AES encryption key securely."""
    if not os.path.exists(KEY_PATH):
        # Generate a new key if one doesn't exist
        key = Fernet.generate_key()
        
        with open(KEY_PATH, "wb") as f:
            f.write(key)
            
        # Attempt to hide the key file on Windows so it isn't accidentally deleted
        try:
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(KEY_PATH, 2) # 2 = Hidden
        except: 
            pass
    else:
        # Read the existing key
        with open(KEY_PATH, "rb") as f:
            key = f.read()
            
    return Fernet(key)

def load_config() -> dict:
    """Loads and decrypts the config file."""
    # Default empty values including the new channel_id
    d = {"webhook_url": "", "bot_token": "", "user_id": "", "channel_id": ""}
    
    if os.path.exists(CONFIG_PATH):
        try:
            cipher = _get_cipher()
            
            # Read the encrypted bytes
            with open(CONFIG_PATH, "rb") as f:
                encrypted_data = f.read()
                
            # Decrypt the bytes back into a JSON string, then parse it into a dictionary
            decrypted_data = cipher.decrypt(encrypted_data).decode("utf-8")
            d.update(json.loads(decrypted_data))
        except Exception as e: 
            print(f"Failed to load config: {e}")
            
    return d

def save_config(cfg: dict):
    """Encrypts and saves the config to a file."""
    try:
        cipher = _get_cipher()
        
        # Convert the dictionary into a formatted JSON string, then into bytes
        json_data = json.dumps(cfg, indent=4).encode("utf-8")
        
        # Encrypt the bytes
        encrypted_data = cipher.encrypt(json_data)
        
        # Save the scrambled bytes to the disk
        with open(CONFIG_PATH, "wb") as f:
            f.write(encrypted_data)
    except Exception as e:
        print(f"Failed to save config: {e}")