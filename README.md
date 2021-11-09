# reddit parser

This is a script for collecting data from posts on reddit.com website.
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

# installation

### *On windows*
1.
    * install python 3 **https://www.python.org/downloads/windows/**
    * install google chrome **https://www.google.com/chrome/**
    * download ChromeDriver **https://chromedriver.chromium.org/downloads**
    * (Important! The chromedriver version should be the same as the chrome browser)*
    * create environment variable in windows named CHROME_DRIVER, value - path to downloaded chromedriver.exe
    * install Git **https://git-scm.com/download/win**
<br><br>

2.  * clone the repo

start console (run -> cmd)

    git clone https://github.com/SergioRyzhov/scrap_1p.git
<br>

3.  * install requirements

in console
    
    pip install -r requirements.txt

# script launch

The script can be run with or without parameters.
The parameters are **number_of_posts** and **filename**.
To run with parameters, you need to specify one or two parameters,
for example:

start console (run -> cmd)

go to the script dir and run it

    python parser.py --number_of_posts=150 --filename=my_filename.txt

the parameters can be omitted, then the default parameters will be used

    number_of_posts=100
    filename=reddit-YYYYMMDDHHmm.txt

The output file will be in the CHROME_DRIVER environment dir.