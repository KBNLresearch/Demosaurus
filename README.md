# Demosaurus

Demo web application: automated support for author attribution (thesaureren) and subject indexing


## Installation

The project runs in Python 3, using Flask (a common webapplication framework for Python). 

In short<br/>
Create a venv: `python3 -m virtualenv /path/to/name-of-venv`<br/>
Activate venv: `source /path/to/name-of-venv/bin/activate`<br/>
In your CLI the line should start with _(name-of-venv)_. You can double check you are using the venv python or pip by typing `which python` or `which pip` (it should show you the path of your virtual environment).<br/>
Now you can install the dependencies in your virtual environment with `pip install -r requirements.txt`.<br/>


## Run

With an activated virtual environment, set the flask environment variables:
`export FLASK_APP=demosauruswebapp` and `export FLASK_ENVIRONMENT=development`
Then, you can run the application calling `flask run`
This starts a development server. Note that in production, it is recommended to use a WSGI server like [Gunicorn](https://gunicorn.org/)


Note that the application requires a pre-filled database with bibliographical metadata (which we are not allowed to openly share all contents of). It is populated using the contents of the dataprocessing directory. Contact us if you have questions or need help. 
Also, note that the application relies on a Rest-API with Annif, which is called upon from the backend as a proxy. 

