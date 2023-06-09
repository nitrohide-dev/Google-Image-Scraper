import os
import tempfile
import unittest

from PIL import Image

import main


class TestCases(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        main.image_path = self.temp_dir.name
        main.search_keys = list({})
        # Parameters
        main.number_of_images = 10
        main.headless = True
        main.min_resolution = (0, 0)
        main.max_resolution = (9999, 9999)
        main.max_missed = 50
        main.number_of_workers = 1
        main.keep_filenames = False

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_run(self):
        main.list = list()
        main.main()
        print(os.listdir(self.temp_dir.name))
        self.assertEqual(len(os.listdir(self.temp_dir.name)), 0)

    def test_one_image(self):
        main.search_keys = list({"cat"})
        main.number_of_images = 1  # Desired number of images
        main.main()
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/cat")), 1)

    def test_two_images(self):
        main.search_keys = list({"dog"})
        main.number_of_images = 2  # Desired number of images
        main.main()
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/dog")), 2)

    def test_long_name(self):
        main.search_keys = list({"shiny rock hd 200 px"})
        main.number_of_images = 2  # Desired number of images
        main.main()
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/shiny rock hd 200 px")), 2)

    def test_two_search_keys(self):
        main.search_keys = list({"cat", "dog"})
        main.number_of_images = 2  # Desired number of images
        main.main()
        self.assertEqual(len(os.listdir(self.temp_dir.name)), 2)
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/dog")), 2)
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/cat")), 2)

    def test_headless_false(self):
        main.headless = False
        main.search_keys = list({"cat"})
        main.number_of_images = 1
        main.main()
        self.assertEqual(len(os.listdir(self.temp_dir.name + "/cat")), 1)

    def test_more_than_100_images_with_multithreading(self):
        main.headless = False
        main.search_keys = list({"cat"})
        main.number_of_images = 220
        main.number_of_workers = 10
        main.main()
        self.assertTrue(len(os.listdir(self.temp_dir.name + "/cat")) >= 200)

    def test_resolution_limits(self):
        main.search_keys = list({"cat"})
        main.min_resolution = (200, 200)
        main.max_resolution = (800, 800)
        main.number_of_images = 50
        main.main()
        for filename in os.listdir(self.temp_dir.name):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                filepath = os.path.join(self.temp_dir.name, filename)
                with Image.open(filepath) as img:
                    resolution = img.size
                    self.assertTrue(main.min_resolution <= resolution <= main.max_resolution,
                                    f"{filename} has an invalid resolution of {resolution}")


if __name__ == '__main__':
    unittest.main()
