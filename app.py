# Version 1.2 9/13/23
import requests, os, random, SteamHandler
from flask import Flask, Response, render_template
app = Flask(__name__)

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))

@app.route('/')
def default():
    return Response(status=200)



@app.route('/dev/test')
def test():
    print(Steam.get_user_summeries("76561197990263870"))
    return Steam.get_user_friend_list("76561198180337238")
@app.route('/main_page_example')
def main_page():
    return render_template("examples/main_page_example.html")
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
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)
