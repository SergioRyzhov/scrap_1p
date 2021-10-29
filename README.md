HOW TO USE IT


=================================   WINDOWS:   ==============

=========Requirements:
- Installed python 3
- Windows OS
- Chrome browser
- Console

=========install:
- First you need to download this parser.py

- Second, you need to download chromedriver https://chromedriver.chromium.org/downloads
for windows OS. The version must be the same like chrome browser.

- Put the unzipped file into the script folder (in folder must be parser.py and chromedriver.exe)

- Open parser.py file by any text redactor. Find the PATH variable at the line 23. Write your path '<script folder>' (for example: PATH = 'D:/Desktop/reddit/')

=========lunch:
- Open powershell

- To lunch script you needs to install some libs:
type:

pip install --upgrade pip

pip install selenium

- Now you can lunch the script:
type:

python "<script folder>\parser.py" (for example: python "D:\Desktop\reddit\parser.py")

When script done it will create .txt file in the same folder.




==================================   Linux:   ==============

=========Requirements:
- Installed python 3
- Linux OS(ubuntu, debian, mint)

=========install:
- First, install Google Chrome for Debian/Ubuntu:
open console and type:

sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo dpkg -i google-chrome*.deb

sudo apt-get install -f

- Now, let’s install xvfb so we can run Chrome headlessly:

type:

sudo apt-get install xvfb

- Now, you need to download this parser_linux.py

- Now, you need to download and install chromedriver https://chromedriver.chromium.org/downloads
for Linux OS.

- Put the unzipped file into the script folder (in folder must be parser_linux.py and chromedriver)

- Open parser.py file by any text redactor. Find the PATH variable at the line 23. Write your path '<script folder>chromedriver' (for example: PATH = '/Home/username/reddit/chromedriver')

=========lunch:
- To lunch you needs to install some Python dependencies and Selenium:
Open console, type:

pip install --upgrade pip 

pip install pyvirtualdisplay selenium

- Now, you can lunch the script:
type:

python3 "<script folder>/parser_linux.py" (for example: python '/home/username/reddit/parser_linux.py')

When script done it will create .txt file in the Home folder.