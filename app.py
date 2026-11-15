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
    '''returns search results for the title that was searched'''
    search = request.args.get('search-title', '')

    with dbi.connect() as conn: 
           movie_results = query.search_by_title(conn, search)
    return render_template('search.html', page_title='Search by Title', 
                           results=movie_results, search_text= search)
    


@app.route('/insert/', methods= ['GET', 'POST'])
def insert_movie():
    '''inserts a new movie row into the movie table with the movie's
        id, title, and release year'''
    id= ""
    title = ""
    year= ""

    if request.method == 'POST': 
        id = request.form.get('movie-tt')
        title = request.form.get('movie-title')
        year = request.form.get('movie-release')

        '''flashes a message and re-renders page if any fields are empty'''
        if not id or not title or not year:
            flash('Please fill in all fields')
            return render_template('insert.html', page_title = 'Insert Movie')


        with dbi.connect() as conn:
         
            if query.check_movie_exists(conn,id):
                '''flashes a message and redirects to a movies update form 
                    if a movie with the inserted tt already exists in the db'''  
                flash(f'Movie already exists')
                return redirect(url_for('update_movie', movie_id= id)) 

            else:
                with dbi.dict_cursor(conn) as curs:
                    curs.execute('''Insert INTO movie(tt,title, `release`)
                    VALUES (%s, %s, %s)''', [id, title, year])
                    conn.commit()

            '''flashes a message and redirects to the inserted movie's update form 
                if inserted successfully'''
            flash('movie added')
            return redirect(url_for('update_movie', movie_id= id))
        
    return render_template('insert.html', page_title='Insert Movie', 
                           id=id, title=title, year= year)


@app.route('/select/', methods = ['GET', 'POST'])
def select_incomplete_movies():
    '''allows users to select incomplete movies from a drop down
        and then click on them to update their details'''
    movie_id = request.form.get('menu-tt', type =int)

    if movie_id is not None:
        return redirect(url_for('update_movie', movie_id=movie_id))
    
    with dbi.connect() as conn:
        incomplete_movies = query.select_incomplete_movies(conn)

    return render_template('select.html', 
                           page_title='Select from Incomplete Movies', 
                           incomplete_movies=incomplete_movies)


@app.route('/update/<int:movie_id>', methods= ['GET', 'POST'])
def update_movie(movie_id):
    '''displays a movie's current information in a form
        and allows users to edit them'''
    with dbi.connect() as conn:
                    with dbi.dict_cursor(conn) as curs: 
                        curs.execute('''Select movie.tt,movie.title, 
                                        movie.`release`, movie.addedby, movie.director 
                                        as director_id, 
                                        person.name as director 
                                        from movie
                                        left join person on movie.director= person.nm 
                                        where movie.tt = %s''', [movie_id])
                        movie_data = curs.fetchone()

                        if movie_data is None:
                            '''flashes message and redirects to insert form if movie with
                                this movie_id is not in the db'''
                            flash(f"Movie with tt = {movie_id} does not exist")
                            return redirect(url_for('insert_movie'))

    if request.method == 'POST':
        action = request.form.get('submit')

        if action =="delete":
             '''deletes a movie row from the db'''
             deleted_title = movie_data.get('title')
             with dbi.connect() as conn:
                  movie_deleted = query.delete_movie(conn, movie_id)
                  flash(f'Movie "{deleted_title}" deleted succesfully')
                  return redirect(url_for('index'))

        
        elif action == 'update':
            '''updates a movie's details'''
            new_title = request.form.get('movie-title')
            new_tt = request.form.get('movie-tt')
            new_year = request.form.get('movie-release')
            new_addedby = request.form.get('movie-addedby')
            new_director = request.form.get('movie-director')
            new_tt = int(request.form.get('movie-tt'))

            with dbi.connect() as conn:
                if new_tt != movie_id and query.check_movie_exists(conn, new_tt):
                    '''flashes message and re-renders page if user attempts to update
                        a movie's id to one that is already in the db'''
                    flash(f'Movie already exists')
                    return render_template('update.html',
                                           page_title='Update Movie Details',
                                           movie=movie_data) 

                updated = query.update_movie(conn, movie_id, new_tt, new_title,
                new_year, new_addedby, new_director)

                if updated and new_tt == movie_id:
                        '''updates movie details'''
                        with dbi.dict_cursor(conn) as curs:
                            curs.execute('''
                                SELECT movie.tt, movie.title, movie.`release`,
                                movie.addedby,
                                movie.director AS director_id,
                                person.name AS director
                                FROM movie
                                LEFT JOIN person ON movie.director = person.nm
                                WHERE movie.tt = %s
                            ''', [movie_id])
                            movie_data = curs.fetchone()

            if not updated:
                '''if update fails, re-render update form'''
                return render_template(
                    'update.html',
                    page_title='Update Movie Details',
                    movie=movie_data
                )

            flash('Movie updated successfully')

            if new_tt != movie_id:
                '''if movie-tt is updated, redirects to new update page
                    with this new movie_id displayed'''
                return redirect(url_for('update_movie', movie_id=new_tt))

    return render_template('update.html', page_title='Update Movie Details', 
                           movie=movie_data)


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
