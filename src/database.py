import sqlite3

DB_FILE = "movies.db"

def init_db():
    """Create the table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_movies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            movie_id    TEXT NOT NULL,
            title       TEXT,
            year        TEXT,
            country     TEXT,
            director    TEXT,
            imdb_rating TEXT,
            saved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_id)   -- no duplicate saves
        )
    ''')
    conn.commit()
    conn.close()


def save_movie(user_id, movie):
    """Save a movie for a user. Ignores if already saved."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO saved_movies
            (user_id, movie_id, title, year, country, director, imdb_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            movie['id'],
            movie['title'],
            movie['year'],
            movie['country'],
            movie['director'],
            movie['imdb_rating'],
        ))
        conn.commit()
        return cursor.rowcount > 0  
    except Exception as e:
        print(f"DB error: {e}")
        return False
    finally:
        conn.close()


def get_saved_movies(user_id):
    """Get all saved movies for a user, newest first."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT movie_id, title, year, country, director, imdb_rating
        FROM saved_movies
        WHERE user_id = ?
        ORDER BY saved_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    movies = []
    for row in rows:
        movies.append({
            'id':          row[0],
            'title':       row[1],
            'year':        row[2],
            'country':     row[3],
            'director':    row[4],
            'imdb_rating': row[5],
        })
    return movies


def delete_saved_movie(user_id, movie_id):
    """Remove a saved movie for a user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM saved_movies
        WHERE user_id = ? AND movie_id = ?
    ''', (user_id, movie_id))
    conn.commit()
    conn.close()