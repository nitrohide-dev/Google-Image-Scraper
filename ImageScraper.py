# import selenium drivers
from PIL.ExifTags import TAGS, GPSTAGS
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# import helper libraries
import time
import urllib.request
from urllib.parse import urlparse
import os
import requests
import io
from PIL import Image
import re

# custom patch libraries
import patch


def get_exif_data(img):
    exif_data = img._getexif()
    if exif_data is None:
        return None
    exif = {}
    gps_data = {}
    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for gps_tag in value:
                gps_decoded = GPSTAGS.get(gps_tag, gps_tag)
                gps_data[gps_decoded] = value[gps_tag]
            exif[decoded] = gps_data
        else:
            exif[decoded] = value
    if gps_data is not None:
        if "GPSLatitude" not in gps_data or "GPSLongitude" not in gps_data:
            return None
        return gps_data


class ImageScraper:

    def __init__(self, url, webdriver_path, image_path, search_image, filter_by_gps, number_of_images=1, headless=True,
                 min_resolution=(0, 0), max_resolution=(1920, 1080), keep_filenames=False, shift=1):
        # check parameter types
        image_path = os.path.join(image_path, search_image)
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        # check if chromedriver is installed
        if (not os.path.isfile(webdriver_path)):
            is_patched = patch.download_lastest_chromedriver()
            if (not is_patched):
                exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")

        options = Options()
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Chrome(webdriver_path, chrome_options=options)
        driver.set_window_size(1400, 1050)

        self.driver = driver
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = url[0]
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.search_key = "image"
        self.keep_filenames = keep_filenames
        self.index = 0
        self.search_image = search_image
        self.filter_by_gps = filter_by_gps

    def save_images(self, image_urls_og, keep_filenames):
        image_urls = image_urls_og[:]

        # last_url = image_urls[:-1]
        # if os.path.exists('last_url.txt'):
        #     os.remove('last_url.txt')
        #     with open('last_url.txt', 'w') as file:
        #         file.write(last_url + " " + len(image_urls) + 1)

        # save images into file directory
        """
          
        """
        print("[INFO] Saving image, please wait...")
        failed_downloads = []
        breakpoint()
        for indx, image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s" % (image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        if get_exif_data(image_from_web) is not None or self.filter_by_gps is False:
                            # if exif_data.items().__contains__()
                            try:
                                if keep_filenames:
                                    # extact filename without extension from URL
                                    o = urlparse(image_url)
                                    image_url = o.scheme + "://" + o.netloc + o.path
                                    name = os.path.splitext(os.path.basename(image_url))[0]
                                    # join filename and extension
                                    filename = "%s.%s" % (name, image_from_web.format.lower())
                                else:
                                    filename = "%s%s.%s" % (
                                        search_string, str(indx), image_from_web.format.lower())

                                image_path = os.path.join(self.image_path, filename)
                                print(
                                    f"[INFO] {self.search_key} \t {indx} \t Image saved at: {image_path}")
                                exif = image_from_web.info.get("exif")
                                if self.filter_by_gps is True:

                                    if image_path.endswith(".gif"):

                                        image_from_web.save(image_path, save_all=True, exif=exif)

                                    else:
                                        image_from_web.save(image_path, exif=exif)
                                else:
                                    if image_path.endswith(".gif"):

                                        image_from_web.save(image_path, save_all=True)

                                    else:
                                        image_from_web.save(image_path)

                            except OSError:
                                rgb_im = image_from_web.convert('RGB')
                                if self.filter_by_gps is True:
                                    if image_path.endswith(".gif"):
                                        rgb_im.save(image_path, save_all=True, exif=exif)
                                    else:
                                        rgb_im.save(image_path, exif=exif)
                                else:
                                    if image_path.endswith(".gif"):
                                        rgb_im.save(image_path, save_all=True)
                                    else:
                                        rgb_im.save(image_path)
                            image_resolution = image_from_web.size
                            if image_resolution is not None:
                                if image_resolution[0] < self.min_resolution[0] or image_resolution[1] < \
                                        self.min_resolution[1] or image_resolution[0] > self.max_resolution[0] or \
                                        image_resolution[1] > self.max_resolution[1]:
                                    image_from_web.close()
                                    os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Download failed: ", e)
                failed_downloads.append(image_url)
                pass
        print("--------------------------------------------------")
        if os.path.exists('failed_downloads.txt'):
            os.remove('failed_downloads.txt')
        if len(failed_downloads) != 0:
            with open('failed_downloads.txt', 'w') as file:
                # Write each string to the file, separated by a new line character
                for index, string in enumerate(failed_downloads):
                    file.write(str(index) + '. ' + string + '\n')
            print(
                f'Please note that some photos might not be downloaded,'
                f' check file "failed_downloads" for such images')
        print(
            f'[INFO] Downloads completed.')

    def check_failed_downloads(self):
        if os.path.exists('failed_downloads.txt'):
            with open('failed_downloads.txt', 'r') as file:
                # Read each line from the file
                lines = file.readlines()
            # Strip each line
            failed_images = [line.split(' ', 1)[1] for line in lines]

            while True:
                self.save_images(failed_images, self.keep_filenames)
                if os.path.exists('failed_downloads.txt'):
                    with open('failed_downloads.txt', 'r') as file:
                        # Read each line from the file
                        lines = file.readlines()
                        if len(lines) == 0:
                            break
                else:
                    break

    def scroll_page_for_links(self):
        # breakpoint()
        elements = []
        while len(elements) < 1000:
            # Scroll down to the bottom of the webpage
            self.driver.execute_script("window.scrollBy(0, window.innerHeight)")

            # Find all the elements matching the xpath

            elements = self.driver.find_elements(By.XPATH, "//a[@class='general-imgcol-item']/img")
            print(len(elements))
            time.sleep(1)

            # text_content = "没有更多"
            # tag_name = "div"
            xpath_expression = "//*[contains(text(), '没有更多') and contains(@class, 'graph-similar-list-bottom-status')]"
            try:
                element = self.driver.find_element_by_xpath(xpath_expression)
                if element is not None:
                    style = element.get_attribute("style")
                    if style == "":
                        break
            except Exception as e:
                pass
        img_links = list(map(lambda x: x.get_attribute("src"), elements))
        return img_links

    def search_for_picture(self):
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[7]/div/span[1]/span[1]')))
        element.click()
        time.sleep(1)

        image_path = os.getcwd() + "/images/" + self.search_image
        file_input_element = self.driver.find_element_by_class_name("general-upload-file")
        file_input_element.send_keys(image_path)

    def run_scraper(self):
        self.search_for_picture()
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/a[1]')))
        image_urls = self.scroll_page_for_links()
        self.driver.quit()
        self.save_images(image_urls,keep_filenames=self.keep_filenames)
