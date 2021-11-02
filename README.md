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
* install google chrome **https://www.google.com/chrome/**
* download ChromeDriver **https://chromedriver.chromium.org/downloads**
*(The version must be the same like chrome browser)*
* download this файл **[GitHub](parser.py)**
* put downloaded file and driver in a folder __c:\reddit\\__
* start console (run -> cmd)
* input **pip install selenium**
* input **pip install bs4**

### *on linux*
* install google chrome **https://www.google.com/chrome/?platform=linux**
* download ChromeDriver **https://chromedriver.chromium.org/downloads** *(for linux)*
*(The version must be the same like chrome browser)*
* download this файл **[GitHub](parser_linux.py)**
* put downloaded file and driver in a folder **/Home/reddit/**
* open console
> **sudo apt-get install xvfb**

> **pip install selenium**

> **pip install bs4**

> **pip install pyvirtualdisplay**

## start script

The script can be run with or without parameters.
The parameters are **number_of_posts** и **filename**.
To run with parameters, you need to specify one or two parameters,
*for example for windows:*
* start console (run -> cmd)
> **python "c:\reddit\parser.py" --number_of_posts=150 --filename=my_filename.txt**

*for example for linux:*
* open console
> **python3 "/home/reddit/parser_linux.py" --number_of_posts=150 --filename=my_filename.txt**

The parameters can be omitted, then the default parameters will be used:
> number_of_posts=100
> filename=reddit-YYYYMMDDHHmm.txt