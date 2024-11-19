import pyautogui
import time
import sys
import os
from datetime import datetime

# Enable PyAutoGUI fail-safe feature
pyautogui.FAILSAFE = True

# Configuration
REFERENCE_IMAGES_DIR = 'ReferenceImages'  # Directory containing reference images
CONFIDENCE = 0.75  # Confidence level for image matching (requires OpenCV)
CHECK_INTERVAL = 1  # Seconds between each check
SEARCH_REGION = None  # (left, top, width, height). Set to None to search the entire screen

# Log File Configuration
LOG_FILE = 'auto_skip_ad.log'

def log(message):
    """Logs a message with timestamp to the log file and prints it."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + '\n')

def load_reference_images(directory):
    """
    Loads all PNG images from the specified directory.

    Args:
        directory: Path to the directory containing reference images.

    Returns:
        A list of file paths to the reference images.
    """
    if not os.path.isdir(directory):
        log(f"Reference images directory '{directory}' not found.")
        sys.exit(1)
    
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.lower().endswith('.png')]
    if not images:
        log(f"No PNG images found in '{directory}'. Please add reference images.")
        sys.exit(1)
    
    log(f"Loaded {len(images)} reference image(s) from '{directory}'.")
    return images

def locate_skip_ad_button(reference_images, region=None):
    """
    Attempts to locate the 'Skip Ad' button on the screen using multiple reference images.

    Args:
        reference_images: List of file paths to reference images.
        region: Optional tuple specifying the region to search (left, top, width, height).

    Returns:
        A tuple of (x, y) screen coordinates if found, else None.
    """
    for img_path in reference_images:
        img_name = os.path.basename(img_path)
        try:
            log(f"Searching for '{img_name}' on the entire screen...")
            # Locate the image on the entire screen with grayscale conversion
            location = pyautogui.locateOnScreen(img_path, confidence=CONFIDENCE, region=region, grayscale=True)
            if location:
                # Get the center of the located region
                center = pyautogui.center(location)
                log(f"'Skip Ad' button found using '{img_name}' at ({center.x}, {center.y}).")
                return center
            else:
                log(f"Reference image '{img_name}' not found on the screen.")
        except Exception as e:
            log(f"Error locating image '{img_name}': {e}")
    log("Skip Ad button not found using any reference image.")
    # Optional: Save a screenshot for debugging
    screenshot_path = 'debug_screenshot.png'
    try:
        pyautogui.screenshot(screenshot_path)
        log(f"Saved debug screenshot as '{screenshot_path}'.")
    except Exception as e:
        log(f"Failed to save debug screenshot: {e}")
    return None

def phantom_click(x, y):
    """
    Sends a mouse click event to the specified (x, y) coordinates without moving the cursor visibly.

    Args:
        x: The x-coordinate of the target.
        y: The y-coordinate of the target.
    """
    try:
        # Get current cursor position
        original_position = pyautogui.position()
        log(f"Original mouse position saved at {original_position}.")

        # Move to the skip button instantly
        pyautogui.moveTo(x, y, duration=0, _pause=False)
        log(f"Moved to 'Skip Ad' button at ({x}, {y}).")
        time.sleep(0.1)  # 100 milliseconds delay

        # Click the button
        pyautogui.click()
        log(f"Clicked 'Skip Ad' button at ({x}, {y}).")

        # Return to original position instantly
        pyautogui.moveTo(original_position.x, original_position.y, duration=0, _pause=False)
        log(f"Returned to original mouse position at {original_position}.")
    except Exception as e:
        log(f"Error in phantom_click: {e}")

def main():
    # Load all reference images
    reference_images = load_reference_images(REFERENCE_IMAGES_DIR)
    
    log("Auto Skip Ad Script Started with Phantom Click.")
    log("Press Ctrl+C or move mouse to top-left corner to terminate the script.")

    try:
        while True:
            button_coords = locate_skip_ad_button(reference_images, region=SEARCH_REGION)
            if button_coords:
                phantom_click(button_coords.x, button_coords.y)
                # Wait to avoid multiple clicks for the same ad
                time.sleep(5)
            else:
                # Optionally, log that no ad was detected
                pass
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        log("Script terminated by user via KeyboardInterrupt.")
    except pyautogui.FailSafeException:
        log("Script terminated by moving mouse to the top-left corner (Fail-Safe Triggered).")
    except Exception as e:
        log(f"Unexpected error: {e}")
    finally:
        log("Auto Skip Ad Script Ended.")

if __name__ == "__main__":
    main()
