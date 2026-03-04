import cv2
import numpy as np

# ---------------------------------
# REAL AI-style cinematic grading
# ---------------------------------
def ai_color(frame):

    # convert to float
    img = frame.astype(np.float32) / 255.0

    # --- Contrast curve (cinematic S-curve)
    img = np.clip(1.2 * (img - 0.5) + 0.5, 0, 1)

    # --- Teal & Orange cinematic tone
    b, g, r = cv2.split(img)

    # shadows → teal
    b = np.clip(b + 0.08, 0, 1)

    # highlights → orange/warm
    r = np.clip(r + 0.12, 0, 1)

    # slight green reduce
    g = np.clip(g * 0.95, 0, 1)

    img = cv2.merge((b, g, r))

    # --- saturation boost
    hsv = cv2.cvtColor((img*255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.25, 0, 255)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # --- vignette effect (cinematic)
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, 600)
    kernel_y = cv2.getGaussianKernel(rows, 600)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()

    for i in range(3):
        img[:,:,i] = img[:,:,i] * mask

    return img
