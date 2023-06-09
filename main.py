import os
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from patch import webdriver_executable
import logging
logging.basicConfig(filename='myapp.log', level=logging.ERROR)


def worker_thread(url):
    image_scraper = GoogleImageScraper(
        url,
        webdriver_path,
        image_path,
        number_of_images,
        headless,
        min_resolution,
        max_resolution)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)

    # Release resources
    del image_scraper


urls = list({"https://www.mafengwo.cn/photo/poi/7048865.html"})
# Define file path
image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))


# Parameters
number_of_images = 2  # Desired number of images
headless = False  # True = No Chrome GUI
min_resolution = (0, 0)  # Minimum desired image resolution
max_resolution = (9999, 9999)  # Maximum desired image resolution
number_of_workers = 10  # Number of threads used
keep_filenames = False  # Keep original URL image filenames

# Run each search_key in a separate thread
# Automatically waits for all threads to finish
# Removes duplicate strings from search_keys

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, urls)


if __name__ == '__main__':
    main()
