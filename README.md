# scraper no. 2 

Same dependencies as previous program

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
       urls                = what albums to download
       headless            = Chrome GUI behaviour. If True, there will be no Chrome window
       min_resolution      = Minimum desired image resolution
       max_resolution      = Maximum desired image resolution
       number_of_workers   = Number of threads
       ```
3. Run the program in the command line (or through an IDE of your choice)
    ```
    python main.py
    ```


 Derived from https://github.com/ohyicong/Google-Image-Scraper