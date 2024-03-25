import requests, os, random, SteamHandler
from json import dumps
from flask import Flask, Response, render_template, redirect, request, send_from_directory
app = Flask(__name__)

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))
web_url = os.environ.get('WEB_URL', 'web_url')


@app.route('/')
def default():
    return render_template("Search Page.html", web_url=web_url)

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

@app.route("/search/")
def search():
    search_query = request.args.get('search')
    search_type = request.args.get('type')
    if str(search_query).isnumeric():
        return redirect(f"{web_url}/user/{search_query}")
    else:
        vanitysearch = Steam.resolve_vanity_url(search_query)
        if vanitysearch['success'] == True:
            return redirect(f"{web_url}/user/{vanitysearch['steamid']}")
        else:
            return Response(404)

#@app.route('/dev/test')
#def test():
#    print(Steam.get_user_summeries("76561197990263870"))
#    return Steam.get_user_friend_list("76561198180337238")

@app.route('/login')
def login():
    return render_template("LoginPage.html")
@app.route('/user/<steamid>')
def user(steamid):
    # Tempory implementation
    #Steam.get_user_stats_for_game(steamid, 1245620)
    # will need to figure out after questions
    #Steam.get_user_inventory(steamid)
    # Steam.get_user_recently_played(steamid, 10)
    # Steam.get_user_group_list(steamid)
    # Steam.get_global_achievement_percentage(1245620)
    # Steam.get_user_steam_level(steamid)
    # Steam.get_user_badges(steamid)
    return render_template("UserPage.html", user=Steam.get_user_summeries([steamid])[steamid], steamid = steamid)
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
    print(games)
    if not games:
        return render_template("examples/game_list_error_example.html", user=Steam.get_user_summeries([steamid])[steamid])
    return render_template("examples/game_list_example.html", games=games)

@app.route("/api/friends")
def game_api():
    try:
        steamid = request.args.get('steamid')
        return Steam.get_user_friend_list(steamid)
    except:
        return Response(
        "Data is Private",
        status=401,
    )
    

@app.route("/api/games")
def friend_api():
    try:
        steamid = request.args.get('steamid')
        return Steam.get_user_owned_games(steamid)
    except:
        return Response(
        "Data is Private",
        status=401,
    )

@app.route('/js/<path:path>')
def send_report(path):
    return send_from_directory('templates/javascript', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)
