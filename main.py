import os
import time

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
        filter_by_gps=filter_by_gps
        , number_of_images=number_of_images)

    image_scraper.run_scraper()
    # Release resources
    del image_scraper
    return True


# Define file path
image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
url = ("https://pic.sogou.com/", "sogou")

# Parameters
headless = False  # True = No Chrome GUI
min_resolution = (0, 0)  # Minimum desired image resolution
max_resolution = (9999, 9999)  # Maximum desired image resolution
keep_filenames = False  # Keep original URL image filenames
number_of_images = 15  # Number of images to download

# PUT IMAGES TO SEARCH IN "images" folder and write their names here
images = ["sogou.jpg", "baidu2.jpeg", "baidutest.jpeg", "gpstest.jpeg"]
filter_by_gps = True  # True = only images with exif GPS data will be saved


def main():
    for image in images:
        if not os.path.exists(os.getcwd() + "/images/" + image):
            print(
                f"[INFO] image {image} not found in /images/ folder. Please, verify that this image is in the folder.")
            continue
        print(f"[INFO] Starting search of {image} ")
        running = True
        while running:
            try:
                result = worker_thread(image)
                if result:
                    running = False
            except Exception as e:
                print(f"[INFO] Bot window or another error detected - restarting current search")
                time.sleep(10)
        print(f"[INFO] Image search of {image} has successfully finished.")
        time.sleep(15)


if __name__ == '__main__':
    main()

