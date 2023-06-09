import os
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from patch import webdriver_executable


def worker_thread(search_key):
    image_scraper = GoogleImageScraper(
        url,
        webdriver_path,
        image_path,
        search_key,
        number_of_images,
        headless,
        min_resolution,
        max_resolution,
        max_missed)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)

    # Release resources
    del image_scraper


# Define file path
image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))

# Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
search_keys = list({"cat"})

# Parameters
number_of_images = 2  # Desired number of images
headless = False  # True = No Chrome GUI
min_resolution = (0, 0)  # Minimum desired image resolution
max_resolution = (9999, 9999)  # Maximum desired image resolution
max_missed = 20  # Max number of failed images before exit
number_of_workers = 10  # Number of threads used
keep_filenames = False  # Keep original URL image filenames

url = "https://www.mafengwo.cn/photo/poi/7048865.html"
# Run each search_key in a separate thread
# Automatically waits for all threads to finish
# Removes duplicate strings from search_keys

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)


if __name__ == '__main__':
    main()
