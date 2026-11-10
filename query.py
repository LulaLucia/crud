# Lula & Cami
import cs304dbi as dbi


def search_by_title(conn, search_text):
    ''' return title, movieID, release year, added by, director ID, director from wmdb '''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT movie.title, movie.tt, movie.`release`, movie.addedby, person.nm, person.name, movie.director
        from movie 
        left join person ON movie.director = person.nm where title like %s ''', ['%' +search_text + '%'])
        
        return curs.fetchall()


def check_movie_exists(conn, movie_tt):
    '''check movies by tt'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT tt from movie where tt= %s''', [movie_tt] )
        row= curs.fetchone()
        return row is not None


def update_movie(conn, movie_id):
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''Delete from movie where tt = %s''', [movie_id])
        conn.commit()



if __name__ == '__main__':
    dbi.conf('cm118_db')
    with dbi.connect() as conn:
        sr = search_by_title(conn, 'hey')
        for movie in sr:
            print(f" {movie['title']}, {movie['tt']},, {movie['release']} ")
  

      
    
