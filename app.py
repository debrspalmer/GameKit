import requests, os, random, SteamHandler
from json import dumps
from flask import Flask, Response, render_template, redirect, request
app = Flask(__name__)

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))
web_url = os.environ.get('WEB_URL', 'web_url')

@app.route("/auth")
def auth_with_steam():
    return render_template("steam_login_redirect.html",redirect_url=Steam.get_openid_url(web_url))
    #return redirect(Steam.get_openid_url(web_url))

@app.route("/authorize")
def authorize():
    user_id=str(request.args['openid.identity']).replace('https://steamcommunity.com/openid/id/','')
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
    return render_template("examples/user_page_example.html", user=Steam.get_user_summeries([steamid])[steamid])
@app.route('/user/<steamid>/friends')
def friend_list(steamid):
    friends = Steam.get_user_friend_list(steamid)
    if not friends:
        return render_template("examples/friend_list_error_example.html", user=Steam.get_user_summeries([steamid])[steamid])
    friends = list(friends.values())
    return render_template("examples/friend_list_example.html", friends=friends)
@app.route('/user/<steamid>/games')
def game_list(steamid):
    games = Steam.get_user_owned_games(steamid)['games']
    if not games:
        return render_template("examples/game_list_error_example.html", user=Steam.get_user_summeries([steamid])[steamid])
    return render_template("examples/game_list_example.html", games=games)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)
