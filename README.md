# Demosaurus

Demo application: automated support for author attribution (thesaureren)


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

Start Demosaurus software by navigating to the Demosaurus directory and typing: `bash start-demosaurus.sh`<br/>
Note: Check if the path to the data (on surfdrive) needs to be modified in _start-demosaurus.sh_ before running.

When finished, stop the Flask server by pressing `Ctrl+C` and exit the virtual environment by typing `deactivate`

