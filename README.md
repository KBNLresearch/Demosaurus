# Demosaurus
Demo application: automated support for author attribution (thesaureren)

# Installation

The project runs in Python 3, using Flask (a common webapplication framework for Python). 
Dependencies are maintained using pipenv. In order to install, make sure Python and pipenv are installed, e.g. follow the steps in https://docs.python-guide.org/dev/virtualenvs/

The command pipenv shell should activate a virtual environment and install all requried dependencies. 
Once the virtual environment is activated, execute Demosaurus/start-demosaurus.sh to set environment variables and let Flask serve the web application (development mode).

When finished, stop the Flask server by pressing Ctrl+C and exit the virtual environment by typing "exit"

