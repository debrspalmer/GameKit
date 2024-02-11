import sqlite3

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            steamid TEXT,
            appid INTEGER,
            name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            steamid TEXT,
            friend_steamid TEXT,
            friend_username TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            steamid TEXT PRIMARY KEY,
            username TEXT
        )
    ''')

    conn.commit()
    conn.close()


def insert_game_data(steamid, games):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM games WHERE steamid = ?', (steamid,))
    existing_games_count = cursor.fetchone()[0]

    if existing_games_count == 0:
        for game in games:
            cursor.execute('''
                INSERT INTO games (steamid, appid, name)
                VALUES (?, ?, ?)
            ''', (steamid, game['appid'], game['name']))

    conn.commit()
    conn.close()

def insert_friend_list(steamid, friends):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM friends WHERE steamid = ?', (steamid,))
    existing_friends_count = cursor.fetchone()[0]

    if existing_friends_count == 0:
        for friend in friends:
            cursor.execute('''
                INSERT INTO friends (steamid, friend_steamid, friend_username)
                VALUES (?, ?, ?)
            ''', (steamid, friend['steamid'], friend['personaname']))

    conn.commit()
    conn.close()
    

def insert_user(user_info, steamid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users WHERE steamid = ?', (steamid,))
    existing_users_count = cursor.fetchone()[0]

    if existing_users_count == 0:
        cursor.execute('''
            INSERT INTO users (steamid, username)
            VALUES (?, ?)
        ''', (steamid, user_info['personaname']))

    conn.commit()
    conn.close()