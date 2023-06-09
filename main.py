import os
import concurrent.futures
from GoogleImageScraper import ImageScraper
from patch import webdriver_executable


def worker_thread(url):
    image_scraper = ImageScraper(
        url=url,
        webdriver_path=webdriver_path,
        image_path=image_path,
        headless=headless,
        min_resolution=min_resolution,
        max_resolution=max_resolution,
        keep_filenames=keep_filenames)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)

    # Release resources
    del image_scraper


# Define file path
image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))


"""
PUT YOUR URL HERE

"""
urls = list({"https://www.mafengwo.cn/photo/poi/7048865.html"})

# Parameters
headless = False  # True = No Chrome GUI
min_resolution = (0, 0)  # Minimum desired image resolution
max_resolution = (9999, 9999)  # Maximum desired image resolution
number_of_workers = 10  # Number of threads used
keep_filenames = False  # Keep original URL image filenames


# Run each url in a separate thread
# Automatically waits for all threads to finish

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, urls)


if __name__ == '__main__':
    main()