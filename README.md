# reddit parser

This is a script for collecting the data from posts on reddit.com website.
What's the data will be collected?
* post URL
* username
* user karma
* user cake day
* post karma
* comment karma
* post date
* number of comments
* number of votes
* post category

At the output, UNIQUE_ID is added by a script.
The script generates a file report with collected data, in the end.

## install required libraries to run the script

### *on windows*
* install python 3 **https://www.python.org/downloads/windows/**
* install google chrome **https://www.google.com/chrome/**
* download ChromeDriver **https://chromedriver.chromium.org/downloads**
*(Important! The chromedriver version should be the same as the chrome browser)*
* download this файл **[GitHub](https://github.com/SergioRyzhov/scrap_1p/blob/multithreading/reddit/parser.py)**
* create environment variable in windows named CHROME_DRIVER, value - path to downloaded chromedriver.exe

start console (run -> cmd)

    pip install requests
    pip install bs4
    pip install selenium

### *on linux*
* install google chrome **https://www.google.com/chrome/?platform=linux**
* download ChromeDriver **https://chromedriver.chromium.org/downloads** *(for linux)*
*(The version must be the same like chrome browser)*
* download this файл **[GitHub](https://github.com/SergioRyzhov/scrap_1p/blob/multithreading/reddit/Linux/parser_linux.py)**
* create environment variable in linux named CHROME_DRIVER, value - path to downloaded chromedriver file

example

    export CHROME_DRIVER='path/to/driver'

open terminal

    sudo apt install python3-pip
    sudo apt-get install xvfb
    pip install pyvirtualdisplay    
    pip install bs4
    pip install selenium    

## start script

The script can be run with or without parameters.
The parameters are **number_of_posts** и **filename**.
To run with parameters, you need to specify one or two parameters,
*for example for windows:*

start console (run -> cmd)

    python "c:\reddit\parser.py" --number_of_posts=150 --filename=my_filename.txt

*for example for linux:*

open terminal

    python3 "/home/reddit/parser_linux.py" --number_of_posts=150 --filename=my_filename.txt

The parameters can be omitted, then the default parameters will be used

    number_of_posts=100
    filename=reddit-YYYYMMDDHHmm.txt

The output file will be in the CHROME_DRIVER environment dir.