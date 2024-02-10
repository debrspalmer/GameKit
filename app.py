import requests, os, random, SteamHandler
from json import dumps
from flask import Flask, Response, render_template, redirect, request
app = Flask(__name__)
import sqlite3

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))
web_url = os.environ.get('WEB_URL', 'web_url')


def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            steamid TEXT,
            appid INTEGER,
            name TEXT,
            playtime INTEGER
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


create_tables()


def insert_game_data(steamid, games):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for game in games:
        cursor.execute('''
            INSERT INTO games (steamid, appid, name, playtime)
            VALUES (?, ?, ?, ?)
        ''', (steamid, game['appid'], game['name'], game['playtime_forever']))

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

@app.route("/auth")
def auth_with_steam():
    return render_template("steam_login_redirect.html", redirect_url=Steam.get_openid_url(web_url))
    #return redirect(Steam.get_openid_url(web_url))

@app.route("/authorize")
def authorize():
    user_id=str(request.args['openid.identity']).replace('https://steamcommunity.com/openid/id/','')
    insert_user(request.args['openid.claimed_id'], user_id)
    #print(request.args)
    return render_template("steam_login_receive_redirect.html",redirect_url=f"{web_url}/user/{user_id}",user_id=user_id)
    #return redirect(f"{web_url}/user/{str(request.args['openid.identity']).replace('https://steamcommunity.com/openid/id/','')}")




@app.route('/')
def default():
    return render_template("examples/main_page_example.html", web_url=web_url)

@app.route('/dev/test')
def test():
    print(Steam.get_user_summeries("76561197990263870"))
    return Steam.get_user_friend_list("76561198180337238")
@app.route('/user/<steamid>')
def user(steamid):
    user_data = Steam.get_user_summeries([steamid])[steamid]
    return render_template("examples/user_page_example.html", user=Steam.get_user_summeries([steamid])[steamid])
@app.route('/user/<steamid>/friends')
def friend_list(steamid):
    friends = Steam.get_user_friend_list(steamid)
    if friends:
        insert_friend_list(steamid, friends)
        friends = list(friends.values())
        return render_template("examples/friend_list_example.html", friends=friends)
    else:
        user_data = Steam.get_user_summeries([steamid])[steamid]
        return render_template("examples/friend_list_error_example.html", user=user_data)
@app.route('/user/<steamid>/games')
def game_list(steamid):
    games = Steam.get_user_owned_games(steamid)['games']
    if games:
        insert_game_data(steamid, games)
        return render_template("examples/game_list_example.html", games=games)
    else:
        user_data = Steam.get_user_summeries([steamid])[steamid]
        return render_template("examples/game_list_error_example.html", user=user_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)