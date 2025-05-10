import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

def upload_image():
    """Open a file dialog for user to choose an image."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Damaged Car Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    return file_path

def create_damage_mask(image, auto=True):
    """Create a damage mask either manually or automatically."""
    if auto:
        # === AUTO: Generate a fixed rectangle as damaged region ===
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        h, w = mask.shape
        cv2.rectangle(mask, (w//3, h//3), (w//2, h//2), 255, -1)
        print("✅ Auto-generated damage mask applied.")
        return mask
    else:
        # === MANUAL: Draw mask with mouse ===
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        drawing = [False]

        def draw(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing[0] = True
            elif event == cv2.EVENT_MOUSEMOVE and drawing[0]:
                cv2.circle(mask, (x, y), 8, 255, -1)
            elif event == cv2.EVENT_LBUTTONUP:
                drawing[0] = False

        cv2.namedWindow("Draw on Damaged Area")
        cv2.setMouseCallback("Draw on Damaged Area", draw)

        while True:
            preview = image.copy()
            preview[mask == 255] = (0, 0, 255)  # Red overlay
            cv2.imshow("Draw on Damaged Area", preview)
            key = cv2.waitKey(1)
            if key in [13, 27]:  # Enter or Esc to finish
                break

        cv2.destroyAllWindows()

        # Show the drawn mask for confirmation
        cv2.imshow("Mask Preview", mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return mask

def inpaint_image(image, mask):
    return cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

def show_results(damaged, restored):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(damaged, cv2.COLOR_BGR2RGB))
    plt.title("Damaged Image")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB))
    plt.title("Restored Image")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

# ========== MAIN EXECUTION ==========

file_path = upload_image()
if not file_path or not os.path.exists(file_path):
    print("❌ No image selected or file does not exist.")
else:
    print(f"📂 Loaded image: {file_path}")
    damaged_image = cv2.imread(file_path)

    # Change this flag to False if you want to manually draw the damage area
    use_auto_mask = True

    damage_mask = create_damage_mask(damaged_image, auto=use_auto_mask)
    restored_image = inpaint_image(damaged_image, damage_mask)
    show_results(damaged_image, restored_image)
