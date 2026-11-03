# Lula & Cami
import cs304dbi as dbi


def search_by_title(conn, search_text):
    ''' return title, movieID, release year, added by, director ID, director from wmdb '''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('SELECT * FROM movie')
        
        return curs.fetchall()



if __name__ == '__main__':
    dbi.conf('ll118_db')
    with dbi.connect() as conn:
        sr = search_by_title(conn)
        for person in sr:
            print('{title}, {tt}, {`release`}')
  

      
    
