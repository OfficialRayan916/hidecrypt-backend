import cv2
from skimage.metrics import structural_similarity as ssim
import math

# Read images
original = cv2.imread("original.png")
encoded = cv2.imread("encoded.png")

# Calculate PSNR
psnr = cv2.PSNR(original, encoded)

# Calculate SSIM
gray_original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
gray_encoded = cv2.cvtColor(encoded, cv2.COLOR_BGR2GRAY)

ssim_score, _ = ssim(gray_original, gray_encoded, full=True)

print(f"PSNR : {psnr:.2f} dB")
print(f"SSIM : {ssim_score:.4f}")