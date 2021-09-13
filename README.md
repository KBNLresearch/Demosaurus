# Demosaurus

Demo web application: automated support for author attribution (thesaureren) and subject indexing


## Installation

The project runs in Python 3, using Flask (a common webapplication framework for Python). 

Dependencies can be viewed in _requirements.txt_ and installed with `pip install -r requirements.txt`.<br/>
Note: Check if you want to create a local venv (virtual environment) before installing the dependencies, see [venv documentation](https://docs.python.org/3.8/library/venv.html) for details.

In short<br/>
Create a venv: `python3 -m venv /path/to/name-of-venv`<br/>
Activate venv: `source /path/to/name-of-venv/bin/activate`<br/>
In your CLI the line should start with _(name-of-venv)_. You can double check you are using the venv python or pip by typing `which python` or `which pip` (it should show you the path of your virtual environment).<br/>
Now you can install the dependencies in your virtual environment.


## Run

With an activated virtual environment, run `demosaurus-webapp/main.py`. 
- It requires a file `demosaurus-webapp/config.txt` that specifies a _SECRET_KEY_, _host_ (IP address to serve the webapp on) and _port_. Set the configuration variables as _\<variable_name\> \<value\>_, each on a new line.
- It requires a pre-filled database with bibliographical metadata (which we are not allowed to openly share all contents of)

