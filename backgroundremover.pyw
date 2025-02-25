import os
import sys
import argparse
from PIL import Image
import cv2
import numpy as np

# ---------------------------
# Background Removal Function
# ---------------------------
def remove_background(input_path, output_path):
    """
    Loads an image from input_path, uses GrabCut to remove the background,
    and saves the result as a PNG with transparency at output_path.
    """
    # Load image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not load image '{input_path}'")
        return False

    height, width = img.shape[:2]
    # Initialize mask, background, and foreground models for GrabCut
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # Define a rectangle slightly inset from the image borders
    rect = (max(1, int(width * 0.05)),
            max(1, int(height * 0.05)),
            width - int(width * 0.1),
            height - int(height * 0.1))
    
    # Run GrabCut
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # Create a binary mask: pixels marked as probable or definite foreground are 1, others 0
    mask2 = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1).astype('uint8')
    
    # Extract foreground
    img_foreground = img * mask2[:, :, np.newaxis]

    # Create an alpha channel (255 for foreground, 0 for background)
    alpha = (mask2 * 255).astype(np.uint8)

    # Combine the BGR image with the alpha channel to get a 4-channel image
    b, g, r = cv2.split(img_foreground)
    rgba = cv2.merge([b, g, r, alpha])

    # Save the resulting image as PNG
    if cv2.imwrite(output_path, rgba):
        return True
    else:
        print(f"Error: Could not write image to '{output_path}'")
        return False

# ---------------------------
# Registry Functions for Context Menu
# ---------------------------
def register_context_menu():
    """
    Registers a context menu entry for .jpg, .jpeg, and .png files under the current user.
    When an image is right-clicked, the "Remove Background" option will appear with an icon.
    """
    try:
        import winreg
    except ImportError:
        print("winreg module is only available on Windows.")
        return

    # Determine the full command: use the current Python executable and this script's full path.
    script_path = os.path.abspath(__file__)
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")  # Use pythonw instead
    # The "%1" will be replaced by the selected file's path.
    command = f'"{python_exe}" "{script_path}" "%1"'
    
    # Path to your icon file - adjust this to wherever you save your icon
    icon_path = os.path.join(os.path.dirname(script_path), "background_remover.ico")
    
    # List of file extensions to register for
    extensions = [".jpg", ".jpeg", ".png", ".webp"]


    for ext in extensions:
        try:
            key_path = rf"Software\Classes\SystemFileAssociations\{ext}\shell\RemoveBackground"
            # Create (or open) the key for the context menu entry.
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Remove Background")
            
            # Add the icon
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            
            winreg.CloseKey(key)
            # Create the command subkey.
            cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path + r"\command")
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)
            winreg.CloseKey(cmd_key)
            print(f"Registered context menu for {ext} files with icon.")
        except Exception as e:
            print(f"Error registering for {ext}: {e}")

def unregister_context_menu():
    """
    Removes the context menu entry for .jpg, .jpeg, and .png files.
    """
    try:
        import winreg
    except ImportError:
        print("winreg module is only available on Windows.")
        return

    extensions = [".jpg", ".jpeg", ".png", ".webp"]


    for ext in extensions:
        try:
            key_path = rf"Software\Classes\SystemFileAssociations\{ext}\shell\RemoveBackground"
            # Delete the 'command' subkey first.
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path + r"\command")
            # Then delete the main key.
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            print(f"Unregistered context menu for {ext} files.")
        except Exception as e:
            print(f"Error unregistering for {ext}: {e}")

# ---------------------------
# Main Entry Point
# ---------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Remove background from an image using OpenCV and optionally register a context menu."
    )
    parser.add_argument("--register", action="store_true", help="Register the context menu entry for image files.")
    parser.add_argument("--unregister", action="store_true", help="Remove the context menu entry for image files.")
    parser.add_argument("file", nargs="?", help="Image file to process.")

    args = parser.parse_args()

    if args.register:
        register_context_menu()
        return
    elif args.unregister:
        unregister_context_menu()
        return
    elif args.file:
        input_file = args.file
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist.")
            return
        # Determine output file name by appending "_nobg" before the extension.
        base, _ = os.path.splitext(input_file)
        output_file = base + "_nobg.png"
        print(f"Processing '{input_file}' -> '{output_file}'")
        if remove_background(input_file, output_file):
            print("Background removal complete.")
        else:
            print("Background removal failed.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
