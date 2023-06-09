# import selenium drivers
import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


class ImageScraper:
    def __init__(self, url, webdriver_path, image_path, number_of_images=1, headless=True,
                 min_resolution=(0, 0), max_resolution=(1920, 1080),keep_filenames=False):
        # check parameter types
        image_path = os.path.join(image_path, "images")
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        # check if chromedriver is installed
        if (not os.path.isfile(webdriver_path)):
            is_patched = patch.download_lastest_chromedriver()
            if (not is_patched):
                exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")

        for i in range(1):
            try:
                # try going to url
                options = Options()
                if headless:
                    options.add_argument('--headless')
                driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                driver.set_window_size(1400, 1050)
                driver.get(url)

            except Exception as e:
                # update chromedriver
                pattern = '(\d+\.\d+\.\d+\.\d+)'
                version = list(set(re.findall(pattern, str(e))))[0]
                is_patched = patch.download_lastest_chromedriver(version)
                if (not is_patched):
                    exit(
                        "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome "
                        "version:https://chromedriver.chromium.org/downloads")

        self.driver = driver
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = url
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.search_key = "image"
        self.keep_filenames = keep_filenames

    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
        """
        wait = WebDriverWait(self.driver, 10)
        image_urls = []
        print("[INFO] Gathering image links")
        self.driver.get(self.url)
        try:
            image_url = self.driver.find_element_by_xpath('/html/body/div[3]/div/ul/li[1]/a[1]').get_attribute("href")
            print(image_url)
            self.driver.get(image_url)
        except Exception as e:
            print(e)
        time.sleep(3)
        search_string = '/html/body/div[3]/div/div[1]/div[1]/ul/li/img'
        running = True
        while running:
            # if len(image_urls) > 10:
            #     new_list = image_urls[:]
            #     asyncio.run(self.save_images(new_list, self.keep_filenames))
            # for _ in range(300):
            time.sleep(0.3)

            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "block-loading _j_stageloading")))
            for i in range(3):
                image = self.driver.find_element_by_xpath(search_string)
                src_link = image.get_attribute("src")
                if src_link is not None and src_link != "None":
                    image_urls.append(src_link)
                    break
                time.sleep(0.2)
            for i in range(3):
                try:
                    button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div[1]/a[2]")
                    button.click()
                    time.sleep(1)
                except Exception as e:
                    print("Button not found.")
                    if i == 2:
                        running = False
                else:
                    break
        self.driver.quit()
        print("[INFO] URL gathering ended")
        return image_urls

    def save_images(self, image_urls_og, keep_filenames):
        image_urls = image_urls_og[:]
        # save images into file directory
        """
          
        """
        print("[INFO] Saving image, please wait...")
        failed_downloads = []
        for indx, image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s" % (image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if (keep_filenames):
                                # extact filename without extension from URL
                                o = urlparse(image_url)
                                image_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(image_url))[0]
                                # join filename and extension
                                filename = "%s.%s" % (name, image_from_web.format.lower())
                            else:
                                filename = "%s%s.%s" % (search_string, str(indx), image_from_web.format.lower())

                            image_path = os.path.join(self.image_path, filename)
                            print(
                                f"[INFO] {self.search_key} \t {indx} \t Image saved at: {image_path}")
                            image_from_web.save(image_path, save_all=True)
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path, save_all=True)
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
