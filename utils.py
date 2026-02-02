import platform
import os
import time
from urllib.parse import urlparse

def play_alert_sound():
    try:
        from playsound import playsound
        # Use a system sound or a bundled file. For now, let's try a system beep first as fallback
        # or a simple frequency beep on Windows
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 1000) # Frequency 1000Hz, Duration 1000ms
        else:
             print('\a') # Terminal bell as fallback
    except Exception as e:
        print(f"Error playing sound: {e}")

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and "zara.com" in result.netloc
    except ValueError:
        return False
