# Google Images.hk scraper

## Pre-requisites:
1. Google Chrome
2. Python3


## Setup:

1. Install Dependencies in terminal 
    ```
    pip install -r requirements.txt
    ```
2. Edit your desired parameters in main.py
    ```
    search_keys         = Strings that will be searched for
    number of images    = Desired number of images
    headless            = Chrome GUI behaviour. If True, there will be no Chrome window
    min_resolution      = Minimum desired image resolution
    max_resolution      = Maximum desired image resolution
    max_missed          = Maximum number of failed image grabs before program terminates. Increase this number to ensure large queries do not exit.
    number_of_workers   = Number of threads
    ```
3. Run the program in the command line (or through an IDE of your choice)
    ```
    python main.py
    ```
   
During the first run, program will download chromedriver, then stop. Simply run the program again after this.

4. Alternatively, you can also run it in Jupyter Notebook through jupyter_main.py 
   


 Derived from https://github.com/ohyicong/Google-Image-Scraper