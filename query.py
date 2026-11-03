# Lula & Cami
import cs304dbi as dbi


def search_by_title(conn, search_text):
    ''' return title, movieID, release year, added by, director ID, director from wmdb '''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''SELECT * FROM movie where title like %s''', ['%' +search_text + '%'])
        
        return curs.fetchall()



if __name__ == '__main__':
    dbi.conf('cm118_db')
    with dbi.connect() as conn:
        sr = search_by_title(conn, 'hey')
        for movie in sr:
            print(f" {movie['title']}, {movie['tt']},, {movie['release']} ")
  

      
    
