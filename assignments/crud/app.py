from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# configure DBI

# For Lookup, use 'wmdb'
# For CRUD and Ajax, use your personal db
# For project work, use your team db

print(dbi.conf('ww123_db'))

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html', page_title='Main Page')

@app.route('/about/')
def about():
    flash('this is a flashed message')
    return render_template('about.html', page_title='About Us')




@app.route('/search/', methods=['GET', 'POST'])
def search_by_title():
    if request.method == 'GET':
        return render_template('search.html', page_title='Search by Title')
    else:
        return redirect(url_for('update'))

@app.route('/insert/')
def insert_movie():
    return render_template('insert.html', page_title='Insert Movie')

@app.route('/select/')
def select_incomplete_movies():
    return render_template('select.html', page_title='Select from Incomplete Movies')

@app.route('/update/<int:tt>')
def update(tt):
    return render_template('update.html', page_title='Update Movie Details')





if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
