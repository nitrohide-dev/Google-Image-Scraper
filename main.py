import os
import concurrent.futures
from ImageScraper import ImageScraper
from patch import webdriver_executable


def worker_thread(search_image):
    image_scraper = ImageScraper(
        search_image=search_image,
        url=url,
        webdriver_path=webdriver_path,
        image_path=image_path,
        headless=headless,
        min_resolution=min_resolution,
        max_resolution=max_resolution,
        keep_filenames=keep_filenames,
        filter_by_gps=filter_by_gps)

    image_scraper.run_scraper()
    # Release resources
    del image_scraper


# Define file path
image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
url = ("https://graph.baidu.com/pcpage/index?tpl_from=pc", "baidu")

# Parameters
headless = False  # True = No Chrome GUI
min_resolution = (0, 0)  # Minimum desired image resolution
max_resolution = (9999, 9999)  # Maximum desired image resolution
keep_filenames = False  # Keep original URL image filenames

# PUT IMAGES TO SEARCH IN "images" folder and write their names here
images = {"DSCN0010.jpg"}
filter_by_gps = True   # True = only images with exif GPS data will be downloaded


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(images)) as executor:
        executor.map(worker_thread, images)


if __name__ == '__main__':
    main()