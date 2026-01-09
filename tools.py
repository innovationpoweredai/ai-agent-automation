# tools.py
import pyautogui
import time
import os
import datetime
import subprocess

# --- NEW: Define a dictionary for known UI element locations ---
# These coordinates are based on your provided list.
# Remember to adjust them if your screen resolution, scaling, or app layout changes.
KNOWN_LOCATIONS = {
    "Whatsapp": (872, 1052),
    "close_application_button": (1893, 12), # For 'X' button on a maximized app
    "minimize_application_button": (1796, 8), # For minimize button on a maximized app
    "chat_gpt_icon": (1027, 1051), # Assuming this is a taskbar icon
    "youtube_icon": (1283, 1054), # Assuming this is a taskbar icon
    "browser_search_bar": (872, 1052), # **CAUTION: This coordinate is identical to 'Whatsapp'. Please verify this is correct for your browser's search bar.**
    "whatsapp_chat_1": (338, 184), # For a specific chat in WhatsApp sidebar
    "whatsapp_chat_2": (382, 248), # For a specific chat in WhatsApp sidebar
    "whatsapp_chat_3": (302, 319), # For a specific chat in WhatsApp sidebar
    "whatsapp_chat_4": (370, 393), # For a specific chat in WhatsApp sidebar
    "windows_search_bar": (576, 1057), # For the search box on the Windows taskbar
}

def take_screenshot(file_path: str) -> str:
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        return f"✅ Saved screenshot: {file_path}"
    except Exception as e:
        return f"❌ Failed to take screenshot: {e}"

def type_text(text: str) -> str:
    try:
        pyautogui.write(text)
        return f"✅ Typed: '{text}'"
    except Exception as e:
        return f"❌ Failed to type text '{text}': {e}"

def click(x: int, y: int) -> str:
    try:
        pyautogui.click(x, y)
        return f"✅ Clicked at ({x},{y})"
    except Exception as e:
        return f"❌ Failed to click at ({x},{y}): {e}"

def click_predefined_location(location_name: str) -> str:
    coords = KNOWN_LOCATIONS.get(location_name)
    if coords:
        try:
            pyautogui.click(coords[0], coords[1])
            return f"✅ Clicked predefined location '{location_name}' at {coords}."
        except Exception as e:
            return f"❌ Failed to click predefined location '{location_name}' at {coords}: {e}"
    else:
        return f"❌ Error: Predefined location '{location_name}' not found in KNOWN_LOCATIONS."

def hotkey(*args: str) -> str:
    try:
        pyautogui.hotkey(*args)
        return f"✅ Pressed hotkey: {args}"
    except Exception as e:
        return f"❌ Failed to press hotkey {args}: {e}"

def open_application(app_path: str) -> str:
    try:
        subprocess.Popen(app_path)
        return f"✅ Launched application: {app_path}"
    except Exception as e:
        return f"❌ Failed to launch application '{app_path}': {e}"

def create_folder(folder_path: str) -> str:
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"✅ Created folder: {folder_path}"
    except Exception as e:
        return f"❌ Failed to create folder '{folder_path}': {e}"

def write_file(file_path: str, content: str) -> str:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Wrote to file: {file_path}"
    except Exception as e:
        return f"❌ Failed to write to file '{file_path}': {e}"

def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"✅ Read from file '{file_path}': {content}"
    except FileNotFoundError:
        return f"❌ File not found: {file_path}"
    except Exception as e:
        return f"❌ Failed to read from file '{file_path}': {e}"

def current_datetime() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def delay(seconds: int) -> str:
    try:
        time.sleep(seconds)
        return f"✅ Delayed execution for {seconds} seconds."
    except Exception as e:
        return f"❌ Failed to delay: {e}"
