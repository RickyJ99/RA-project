import pytesseract
from PIL import Image, ImageEnhance

# Load the captcha image
captcha_image = Image.open("captcha.png")

# Enhance the image by increasing contrast
enhancer = ImageEnhance.Contrast(captcha_image)
captcha_image = enhancer.enhance(2)  # Increase the contrast by a factor of 2

# Convert the image to grayscale
captcha_image = captcha_image.convert("L")

# Apply a threshold to improve contrast
threshold_value = 181
captcha_image_bw = captcha_image.point(lambda x: 0 if x < threshold_value else 255, "1")

# Extract text from the captcha image
captcha_text = pytesseract.image_to_string(captcha_image_bw)

# Print the extracted text
print(": Captcha Text:", captcha_text)
