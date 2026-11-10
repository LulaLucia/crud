from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
import query

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# configure DBI

# For Lookup, use 'wmdb'
# For CRUD and Ajax, use your personal db
# For project work, use your team db

print(dbi.conf('ll118_db'))

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html', page_title='Main Page')

@app.route('/about/')
def about():
    flash('this is a flashed message')
    return render_template('about.html', page_title='About Us')


@app.route('/search/', methods=['GET'])
def search_by_title():
    search = request.args.get('search', '')

    with dbi.connect() as conn: 
           movie_results = query.search_by_title(conn, search)
    return render_template('search.html', page_title='Search by Title', results=movie_results, search_text= search)
    


@app.route('/insert/', methods= ['GET', 'POST'])
def insert_movie():
    id= ""
    title = ""
    year= ""
    
    if request.method == 'POST': 
        id = request.form.get('movie_id')
        title = request.form.get('movie_title')
        year = request.form.get('release_year')

        with dbi.connect() as conn:
            if query.check_movie_exists(conn,id):
                flash(f'error: movie exists; Movie with tt = {id} is already in database.')
                return redirect(url_for('update_movie', movie_id= id, title=title, year=year)) #update here so that it redirects it to update movie

            with dbi.dict_cursor(conn) as curs:
                curs.execute('''Insert INTO movie(tt,title, `release`)
                VALUES (%s, %s, %s)''', [id, title, year])
                conn.commit()

        flash('movie added')
        return redirect(url_for('update_movie', movie_id= id))
    return render_template('insert.html', page_title='Insert Movie', id=id, title=title, year= year)


@app.route('/select/', methods=['GET'])
def select_incomplete_movies():
    movie_id = request.args.get('drop', type =int)

    if movie_id is not None:
        return redirect(url_for('update_movie', movie_id=movie_id))
    
    with dbi.connect() as conn:
        incomplete_movies = query.select_incomplete_movies(conn)

    return render_template('select.html', page_title='Select from Incomplete Movies', incomplete_movies=incomplete_movies)


@app.route('/update/<int:movie_id>', methods= ['GET', 'POST'])
def update_movie(movie_id):
    with dbi.connect() as conn:
                    with dbi.dict_cursor(conn) as curs: 
                        curs.execute('''Select movie.tt,movie.title, movie.`release`, movie.addedby, movie.director as director_id, person.name as director 
                                    from movie
                                        left join person on movie.director= person.nm where movie.tt = %s''', [movie_id])
                        movie_data = curs.fetchone()
                      
                        if movie_data is None:
                            flash(f"Movie with tt = {movie_id} does not exist")
                            return redirect(url_for('insert_movie'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action =="delete":
             deleted_title = movie_data['title']
             with dbi.connect() as conn:
                  movie_deleted = query.delete_movie(conn, movie_id)
                  flash(f'Movie "{deleted_title}" deleted succesfully')
                  return redirect(url_for('insert_movie'))

        elif action == 'update':
            new_title = request.form.get('movie_title')
            # new_year = request.form.get('year')
            # new_addedby = request.form.get('addedby')
            # new_director_id = request.form.get('director_id')
            with dbi.connect() as conn:
                query.update_movie(conn, movie_id)
                # with dbi.dict_cursor(conn) as curs:
                #           curs.execute('''UPDATE movie set title = %s, `release` = %s, addedby = %s, director = %s WHERE tt= %s''',[ new_title, new_year,  new_addedby, new_director_id, movie_id])
                #           conn.commit()
                #           flash(f'Movie "{new_title}" updated')
                return redirect(url_for('insert_movie'))
                
    return render_template('update.html', page_title='Update Movie Details', movie=movie_data)


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
