# Lula & Cami
import cs304dbi as dbi
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

def search_by_title(conn, search_text):
    ''' return title, movieID, release year, added by, director ID, director from wmdb '''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT movie.title, movie.tt, movie.`release`, movie.addedby, person.nm, person.name, movie.director
        from movie 
        left join person ON movie.director = person.nm where title like %s ''', ['%' +search_text + '%'])
        
        return curs.fetchall()

def select_incomplete_movies(conn):
    ''' return title, movieID, release year, added by, director ID, director from wmdb '''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT * FROM movie where director is null or `release` is null''')
        
        return curs.fetchall()


def check_movie_exists(conn, movie_tt):
    '''check movies by tt'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT tt from movie where tt= %s''', [movie_tt] )
        row= curs.fetchone()
        return row is not None


def delete_movie(conn, movie_id):
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''Delete from movie where tt = %s''', [movie_id])
        conn.commit()
        

def update_movie(conn, movie_id, new_tt): # CHANGED
    new_title = request.form.get('movie-title')
    new_year = request.form.get('movie-release')
    new_addedby = request.form.get('movie-addedby')
    new_director = request.form.get('movie-director')

    if not new_director or new_director.strip().lower() == 'none':
        new_director_id = None
    else:
        new_director_id = new_director

    if new_addedby == 'None' or new_addedby == 'null':
        new_addedby = None

    elif new_addedby == "none" or new_addedby == "Null":
        flash('addedby needs to be "None" or "null" exactly')
        return False 

    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            UPDATE movie
            SET tt = %s, title = %s, `release` = %s,
                addedby = %s, director = %s
            WHERE tt = %s
        ''', [new_tt, new_title, new_year, new_addedby, new_director_id, movie_id]) 

        conn.commit()

    return True
                                  

if __name__ == '__main__':
    dbi.conf('cm118_db')
    with dbi.connect() as conn:
        sr = search_by_title(conn, 'hey')
        for movie in sr:
            print(f" {movie['title']}, {movie['tt']},, {movie['release']} ")
  

      
    
