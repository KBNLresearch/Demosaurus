import sqlite3

from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.set_trace_callback(print) # logs in print
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    True
    #db = get_db()
    #with current_app.open_resource('schema.sql') as f:
    #    db.executescript(f.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close_db)

