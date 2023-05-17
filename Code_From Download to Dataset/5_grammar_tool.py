import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from io import BytesIO
import time
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance
import pandas as pd

import subprocess


def check_ping():
    target_host = "141.225.61.35"  # Replace with your desired host or IP address
    command = [
        "ping",
        "-c",
        "1",
        target_host,
    ]  # Adjust the parameters based on your system

    while True:
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            print("Ping successful!")
            break
        except subprocess.CalledProcessError as e:
            # Ping failed, wait and try again
            print("Ping failed. Retrying...")
            continue


# Call the function to start the ping check
check_ping()

df = pd.read_csv(
    "/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/Data/4_Data_with_AI_Market_Indicies.csv",
    sep=",",
)
df["Date Time"] = pd.to_datetime(df["Date Time"], format="%Y-%m-%d %H:%M:%S%z")


trump_2020 = df[
    (df["Date Time"].dt.year == 2020)
    & (df["Date Time"].dt.month < 9)
    & (df["Title"].str.contains("Press Bri"))
    & (df["Administration"].str.contains("Trump"))
].loc[:, :]

trump_2020.head(5)
# Create a new Chrome browser instance and navigate to the website
browser = webdriver.Chrome()
browser.maximize_window()
availability = False
for text in trump_2020.loc[trump_2020.index, "Main text"]:
    while not availability:
        browser.get("http://141.225.61.35/CohMetrix2017/")

        # Wait for the website to load and locate the text area element
        time.sleep(5)
        text_area = browser.find_element("id", "Text")

        # Enter the speech text into the text area and submit the form
        text_area.send_keys(text)

        captcha_text = ""
        while not captcha_text:
            # Find the captcha image and download it
            captcha_image_element = browser.find_element(
                "xpath", "//img[@src='/CohMetrix2017/Default/GetCaptchaImage']"
            )

            # Get the location and size of the captcha image element
            location = captcha_image_element.location
            size = captcha_image_element.size

            # Get the screenshot of the entire page
            screenshot = browser.get_screenshot_as_png()

            # Create a PIL Image object from the screenshot
            screenshot_image = Image.open(BytesIO(screenshot))

            # Calculate the coordinates of the captcha image in the screenshot
            left = 294
            top = 900
            right = 891
            bottom = 1050

            # Crop the screenshot to extract the captcha image
            captcha_image = screenshot_image.crop((left, top, right, bottom))

            # Save the captcha image
            captcha_image.save("captcha.png")

            # Load the image
            image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)

            # Apply thresholding to convert the image into binary (black and white)
            _, binary_image = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY)

            # Apply morphological operations to remove the grid lines
            kernel = np.ones((3, 3), np.uint8)
            cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

            # Enhance the image by increasing contrast
            enhancer = ImageEnhance.Contrast(Image.fromarray(cleaned_image))
            cleaned_image = enhancer.enhance(
                2
            )  # Increase the contrast by a factor of 2

            # Convert the cleaned image to a numpy array
            cleaned_image_np = np.array(cleaned_image)

            # Remove small dots (assumed to be noise) using erosion and dilation
            kernel = np.ones((3, 3), np.uint8)
            cleaned_image_np = cv2.erode(cleaned_image_np, kernel, iterations=1)
            cleaned_image_np = cv2.dilate(cleaned_image_np, kernel, iterations=1)

            # Save the cleaned image
            cleaned_image = Image.fromarray(cleaned_image_np)
            cleaned_image.save("cleaned_captcha.png")

            # Grayscale, Gaussian blur, Otsu's threshold
            image = cv2.imread("cleaned_captcha.png")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (3, 3), 0)
            thresh = cv2.threshold(
                blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )[1]

            # Morph open to remove noise and invert image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            invert = 255 - opening

            # Load the captcha image
            captcha_image = Image.open("cleaned_captcha.png")

            # Extract text from the captcha image
            captcha_text = pytesseract.image_to_string(
                invert,
                config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm",
            )

            # Print the extracted text
            print("Captcha Text:", captcha_text)

            text_area_captcha = browser.find_element("id", "CaptchaText")
            text_area_captcha.send_keys(captcha_text)

            try:
                # Check if the captcha validation failed
                validation_failed = browser.find_element(
                    "xpath",
                    '//*[@style="border: 0px solid rgb(141, 27, 27); width:300px;color:red;padding: 5px;"]',
                )
                if validation_failed:
                    captcha_text = ""  # Reset captcha text if validation failed
            except NoSuchElementException:
                print("I did it")
        # Print the extracted text
        print("Captcha Text:", captcha_text)
        # Reset captcha text if validation failed

        availability = True
input("press key...")
