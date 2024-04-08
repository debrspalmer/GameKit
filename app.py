import requests, os, random, SteamHandler
from json import dumps
from flask import Flask, Response, render_template, redirect, request, send_from_directory
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

Steam = SteamHandler.Steam(os.environ.get('STEAM_KEY', 'Steam_api_key'))
web_url = os.environ.get('WEB_URL', 'web_url')
production = os.environ.get('PRODUCTION', False)

@app.route('/')
def default():
    return render_template("Search_Page_Account.html", web_url=web_url)

@app.route("/auth")
def auth_with_steam():
    return render_template("steam_login_redirect.html",redirect_url=Steam.get_openid_url(web_url))
    #return redirect(Steam.get_openid_url(web_url))

@app.route("/about")
def about():
    return render_template("About_Us.html")

@app.route("/contact")
def contact():
    return render_template("Contact_Us.html")

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
        print(vanitysearch)
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
    # will need to figure out after questions
    #Steam.get_user_inventory(steamid)
    #Steam.get_user_recently_played(steamid, 10)
    #Steam.get_user_group_list(steamid)
    #Steam.get_global_achievement_percentage(1086940)
    #Steam.get_user_achievements_per_game(steamid, 1086940)
    #Steam.get_user_stats_for_game(steamid, 1086940)
    #Steam.get_user_steam_level(steamid)
    #Steam.get_user_badges(steamid)
    return render_template("User_Page.html", user=Steam.get_user_summeries([steamid])[steamid], steamid = steamid)
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
    steamid = request.args.get('steamid')
    data = Steam.get_user_friend_list(steamid)
    if data == False:
        return Response(
        "Data is Private",
        status=401,
    )
    else:
        return data
        
@app.route("/api/groups")
def groups_api():
    try:
        steamid = request.args.get('steamid')
        response = []
        response = Steam.get_user_group_list(steamid)
        return {'Response':response}
    except:
        return Response(
        "Data is Private",
        status=401,
    )

@app.route("/api/achievments")
def achievments_api():
    try:
        steamid = request.args.get('steamid')
        appid = request.args.get('appids')
        appids = appid.split(',')
        response = []
        for appid in appids:
            appachievment = Steam.get_user_achievements_per_game(steamid, appid)
            response.append(appachievment)
            print(appachievment,'\n\n\n')
        return {'Response':response}
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
def send_js(path):
    return send_from_directory('templates/javascript', path)
@app.route('/stylesheets/<path:path>')
def send_stylesheets(path):
    return send_from_directory('templates/stylesheets', path)
@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('templates/images', path)

@scheduler.task('interval', id='clear_cache', hours=1)
def clear_cache():
    Steam.db_manager.clear_cache()

@scheduler.task('interval', id='clear_users_table', days=7)
def clear_users_table():
    Steam.db_manager.clear_users_table()

@scheduler.task('interval', id='clear_friends_table', days=7)
def clear_friends_table():
    Steam.db_manager.clear_friends_table()

@scheduler.task('interval', id='clear_user_games_table', days=2)
def clear_user_games_table():
    Steam.db_manager.clear_user_games_table()

@scheduler.task('interval', id='clear_user_groups_table', days=7)
def clear_user_groups_table():
    Steam.db_manager.clear_user_groups_table()

@scheduler.task('interval', id='clear_user_level_table', days=7)
def clear_user_level_table():
    Steam.db_manager.clear_user_level_table()

@scheduler.task('interval', id='clear_badges_table', days=7)
def clear_badges_table():
    Steam.db_manager.clear_badges_table()

@scheduler.task('interval', id='clear_achievement_percentages_table', days=1)
def clear_achievement_percentages_table():
    Steam.db_manager.clear_achievement_percentages_table()

@scheduler.task('interval', id='clear_achievements_table', days=1)
def clear_achievements_table():
    Steam.db_manager.clear_achievements_table()

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()  
    if production:
        app.run(host="0.0.0.0")
    else: 
        app.run(host="0.0.0.0", port=3000, debug = True)
