# reddit parser with api

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

First of all you must run the server.py script

start console (run -> cmd)

    python server.py

The second part is to run parser.py script

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

# API endpoints

* `GET http://<host_name>:<port>/posts/ `
Returns content of the entire file in JSON format. If you just started the server, you have to run parser.py first.

For example
    
    requests.get('<host_name>:<port>/posts/')

* `GET http://<host_name>:<port>/posts/UNIQUE_ID/`
Returns content of this post in JSON format.

For example

    requests.get('<host_name>:<port>/29e8b643-43a4-11ec-96c9-50e5493f093d')

* `POST http://<host_name>:<port>/posts/`
Add new line with a new UNIQUE_ID into the file.

For example

    requests.post('<host_name>:<port>/posts/')

* `DELETE http://<host_name>:<port>/posts/UNIQUE_ID/`
Delete the line with a UNIQUE_ID in the file.

For example

    requests.delete('<host_name>:<port>/posts/29e8b643-43a4-11ec-96c9-50e5493f093d')

* `PUT http://<host_name>:<port>/posts/UNIQUE_ID/`
Change the post with a UNIQUE_ID in the file. Need put change information in JSON format.

For example

    requests.put('<host_name>:<port>/posts/29e8b643-43a4-11ec-96c9-50e5493f093d',data=json.dumps({'post category': 'antiwork'}), verify=False)