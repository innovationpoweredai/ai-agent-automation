import pyautogui

# Take a screenshot
im = pyautogui.screenshot()

# Save the screenshot to AGENT_DIR
im.save(r"AGENT_DIR")

print("Screenshot saved to AGENT_DIR")
