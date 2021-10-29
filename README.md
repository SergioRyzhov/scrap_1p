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