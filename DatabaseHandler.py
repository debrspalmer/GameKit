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
            friend_steamid TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            steamid TEXT PRIMARY KEY
        )
    ''')

    conn.commit()
    conn.close()

def insert_game_data(steamid, games):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for game in games:
        cursor.execute('''
            INSERT INTO games (steamid, appid, name,)
            VALUES (?, ?, ?, ?)
        ''', (steamid, game['appid'], game['name']))

    conn.commit()
    conn.close()

def insert_friend_list(steamid, friends):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for friend in friends:
        cursor.execute('''
            INSERT INTO friends (steamid, friend_steamid)
            VALUES (?, ?)
        ''', (steamid, friend['steamid']))

    conn.commit()
    conn.close()


def insert_user(username, steamid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (username, steamid)
        VALUES (?, ?)
    ''', (username, steamid))

    conn.commit()
    conn.close()

