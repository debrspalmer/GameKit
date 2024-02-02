# Version 1.2 9/13/23
import requests, os, random, SteamHandler
from flask import Flask, Response, render_template
app = Flask(__name__)

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))

@app.route('/')
def default(run=0,error=False):
    return Response(status=200)
@app.route('/test')
def test(run=0,error=False):
    return Steam.get_user_friend_list("76561198180337238")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)
