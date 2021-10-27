HOW TO USE IT

=========Requirements:
- Installed python 3
- Windows OS
- Console

=========install:
- You need dounload chromewebdriver https://chromedriver.chromium.org/downloads
for your OS. The version must be the same like crome webbrowser.

- Put the unzipped file into the script folder (in folder must be parser.py and chromedriver.exe)

=========lunch:
- Open powershell

- To lunch script type:
pip install selenium

python "<script folder>\parser.py"
(For example: python "c:\reddit\parser.py")

-If you see the message "ERROR:root:Not the right path" you should input full path to chromedriver.exe
(For example: 	ERROR:root:Not the right path
		Input path to chromedriver: c:/reddit/chromedriver.exe)

When script done it created .txt file in the same folder.