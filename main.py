from ai_model import ai_color
import cv2

print("AI IMAGE COLOR GRADING STARTED...")

# -------------------------------
# STEP 1: Read image
# -------------------------------
img = cv2.imread("input.png")

if img is None:
    print("Error: input.png not found")
    exit()

print("Image loaded successfully")


# -------------------------------
# STEP 2: Cinematic color function
# -------------------------------
def cinematic_color(frame):

    # Contrast + brightness
    frame = cv2.convertScaleAbs(frame, alpha=1.25, beta=20)

    # Warm cinematic tone
    b, g, r = cv2.split(frame)
    r = cv2.add(r, 30)     # boost red
    g = cv2.add(g, 5)      # slight green
    frame = cv2.merge((b, g, r))

    # Slight sharpening (cinematic clarity)
    kernel = [[0,-1,0],
              [-1,5,-1],
              [0,-1,0]]
    import numpy as np
    kernel = np.array(kernel)
    frame = cv2.filter2D(frame, -1, kernel)

    return frame


# -------------------------------
# STEP 3: Apply grading
# -------------------------------
graded_img = ai_color(img)



# -------------------------------
# STEP 4: Save output
# -------------------------------
cv2.imwrite("output.jpg", graded_img)

print("DONE ✅")
print("Output saved as output.jpg")
