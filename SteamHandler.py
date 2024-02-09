import requests
from urllib.parse import urlencode

class Steam:
    def __init__(self, key):
        self.STEAM_KEY = key
        self.cache = {
            'user_summeries': {},
            'user_friend_list': {},
            'user_achievements': {},
            'user_stats_for_game': {},
            'user_owned_games': {},
            'user_recently_played': {},
            'app_news': {},
            'game_global_achievement': {},
            'app_details': {},
        }

    # OpenID
    def get_openid_url(self,web_url):
        steam_openid_url = 'https://steamcommunity.com/openid/login'
        params = {
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.mode': 'checkid_setup',
        'openid.return_to': f'{web_url}/authorize',
        'openid.realm': f'{web_url}'
        }

        query_string = urlencode(params)
        auth_url = steam_openid_url + "?" + query_string
        return(auth_url)

    # User API Calls
    def get_user_steamid(self, username):
        # Implement caching for this method if needed
        pass

    def get_user_summeries(self, steamids):
        result = {}

        # Identify which steamids are not in the cache
        not_cached_steamids = [steamid for steamid in steamids if steamid not in self.cache['user_summeries']]

        if not_cached_steamids:
            # Make one request for all not cached steamids
            response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.STEAM_KEY}&steamids={','.join(not_cached_steamids)}")
            data = response.json()

            # Update the cache with the new data
            for user in data["response"]["players"]:
                self.cache['user_summeries'][user["steamid"]] = user

        # Retrieve data from cache for all steamids
        for steamid in steamids:
            result[steamid] = self.cache['user_summeries'][steamid]

        return result

    def get_user_friend_list(self, steamid):
        if steamid in self.cache['user_friend_list']:
            return self.cache['user_friend_list'][steamid]

        response = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={self.STEAM_KEY}&steamid={steamid}&relationship=friend")
        if not "friendslist" in response.json():
            print(response.json(), "Error getting friends data")
            return False
        friend_ids = [i['steamid'] for i in response.json()["friendslist"]["friends"]]
        data = self.get_user_summeries(friend_ids)
        self.cache['user_friend_list'][steamid] = data
        return data

    def get_user_achievements(self, steamid, appid):
        cache_key = f"achievements_{steamid}_{appid}"
        if cache_key in self.cache['user_achievements']:
            return self.cache['user_achievements'][cache_key]

        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
        data = response.json()
        self.cache['user_achievements'][cache_key] = data
        return data

    def get_user_stats_for_game(self, steamid,appid):
        cache_key = f"stats_{steamid}_{appid}"
        if cache_key in self.cache['user_stats_for_game']:
            return self.cache['user_stats_for_game'][cache_key]
        
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
        data = response.json()
        self.cache['user_stats_for_game'][cache_key] = data
        return data

    def get_user_owned_games(self, steamid):
        if steamid in self.cache['user_owned_games']:
            return self.cache['user_owned_games'][steamid]
        
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&include_appinfo=true&format=json")
        data = response.json()['response']
        self.cache['user_owned_games'][steamid] = data
        return data

    def get_user_recently_played(self, steamid,count):
        # Implement cache
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&count={count}&format=json")
        return response.json()["friendslist"]

    def get_global_achievement_percentage(self, appid):
        if appid in self.cache['game_global_achievement']:
            return self.cache['game_global_achievement'][appid]
        
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}&format=xml")
        data = response.json()['response']
        self.cache['game_global_achievement'][appid] = data
        return data
    
    def resolve_vanity_url(self, vanityurl):
        vanityurl = str(vanityurl).replace("https://steamcommunity.com/id/", "").replace("/", "")
        response = requests.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={self.STEAM_KEY}&vanityurl={vanityurl}")
        return response["response"]

    # Game API Calls
    def get_app_details(self, appids):
        result = {}

        # Identify which steamids are not in the cache
        not_cached_appids = [appid for appid in appids if appid not in self.cache['app_details']]

        if not_cached_appids:
            # Make one request for all not cached steamids
            response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.STEAM_KEY}&steamids={','.join(not_cached_appids)}")
            data = response.json()

            # Update the cache with the new data
            for app in data:
                    if app['success']:
                        self.cache['app_details'][app['data']["steam_appid"]] = app

        # Retrieve data from cache for all steamids
        for app in appids:
            result[app] = self.cache['app_details'][app]

        return result

    def get_app_news(self, appid,count=3,maxlength=300):
        if appid in self.cache['app_news']:
            return self.cache['app_news'][appid]
        
        response = requests.get(f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count={count}&maxlength={maxlength}&format=json")
        data = response.json()['response']
        self.cache['app_news'][appid] = data
        return data

    def clear_cache(self):
        for cache_key in self.cache:
            self.cache[cache_key] = {}
