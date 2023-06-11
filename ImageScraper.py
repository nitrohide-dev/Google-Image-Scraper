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

    def __init__(self, url, webdriver_path, image_path, number_of_images=1, headless=True,
                 min_resolution=(0, 0), max_resolution=(1920, 1080), keep_filenames=False, shift=1):
        # check parameter types
        image_path = os.path.join(image_path, url[1])
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
                driver.get(url[0])

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
        self.url = url[0]
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.search_key = "image"
        self.keep_filenames = keep_filenames
        self.shift = shift
        self.total_images = int(driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/span/i').text)
        self.last_url = self.url
        self.index = 0

    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
        """
        wait = WebDriverWait(self.driver, 10)
        image_urls = []
        print("[INFO] Gathering image links")

        try:
            self.driver.get(self.url)
            image_url = self.driver.find_element_by_xpath('/html/body/div[3]/div/ul/li[1]/a[1]').get_attribute("href")
            self.driver.get(image_url)
        except Exception as e:
            print(e)
            self.driver.get(self.url)
        time.sleep(3)
        search_string = '/html/body/div[3]/div/div[1]/div[1]/ul/li/img'
        running = True
        self.index = 0 + self.shift
        # for i in range(500):
        while running:
            self.last_url = self.driver.current_url
            self.index += 1
            progress_pct = self.index / self.total_images * 100
            if self.index % 100 == 0:
                print(f"Progress: {self.index}/{self.total_images} ({progress_pct:.1f}%)")
            # if len(image_urls) > 10:
            #     new_list = image_urls[:]
            #     asyncio.run(self.save_images(new_list, self.keep_filenames))
            # for _ in range(100):
            time.sleep(0.3)
            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "block-loading _j_stageloading")))
            for i in range(3):
                image = self.driver.find_element_by_xpath(search_string)
                src_link = image.get_attribute("src")
                if src_link is not None and src_link != "None":
                    image_urls.append(src_link)
                    break
                time.sleep(0.2)
            for i in range(10):
                try:
                    button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div[1]/a[2]")
                    button.click()
                    break
                except Exception as e:
                    time.sleep(1)
                    if i == 9:
                        running = False
        self.driver.quit()
        print("[INFO] URL gathering ended")
        return image_urls

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
        for indx, image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s" % (image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        if get_exif_data(image_from_web) is not None:
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
                                        search_string, str(indx + self.shift), image_from_web.format.lower())

                                image_path = os.path.join(self.image_path, filename)
                                print(
                                    f"[INFO] {self.search_key} \t {indx + self.shift} \t Image saved at: {image_path}")
                                if image_path.endswith(".gif"):

                                    image_from_web.save(image_path, save_all=True, exif=image_from_web.info.get("exif"))

                                else:
                                    image_from_web.save(image_path, exif=image_from_web.info.get("exif"))

                            except OSError:
                                rgb_im = image_from_web.convert('RGB')
                                if image_path.endswith(".gif"):
                                    rgb_im.save(image_path, save_all=True, exif=rgb_im.info.get("exif"))
                                else:
                                    rgb_im.save(image_path, exif=rgb_im.info.get("exif"))
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

        self.shift += len(image_urls)

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
        elements = []
        while len(elements) < 1000:
            # Scroll down to the bottom of the webpage
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.END).perform()
            time.sleep(1)

            # Find all the elements matching the xpath
            elements = self.driver.find_elements(By.CLASS_NAME, "general-imgcol-item")
            print(len(elements))
        pass

    def run_scraper(self):
        self.driver.get("https://graph.baidu.com/s?sign=1267819133b6badfea32501686460968&f=all&tn=pc&tn=pc&idctag=gz&idctag=gz&sids=&sids=&logid=2823725675&logid=2823725675&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&session_id=3291421184242315508&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general")
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/a[1]')))
        image_urls = self.scroll_page_for_links()


