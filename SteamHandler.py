import requests
from urllib.parse import urlencode
import Database.DatabaseHandler as Database

class Steam:
    def __init__(self, key):
        self.STEAM_KEY = key
        self.cache = {
            #'user_summeries': {},
            #'user_friend_list': {},
            #'user_achievements_per_game': {},
            #'user_stats_for_game': {},
            #'user_owned_games': {},
            'user_recently_played': {}, # to be implemented
            'app_news': {}, # to be removed caching wise
            'game_global_achievement': {}, # to be implemented
            'app_details': {}, # to be removed completely
            'user_inventory': {}, # will need to be addressed 
            'user_groups': {}, # to be implemented
            'user_level': {},  # to be implemented
            'user_badges': {} # to be implemented
        }
        self.db_manager = Database.DatabaseManager('database.db')
        self.db_achievements = Database.DatabaseManager('achievements.db')
        self.db_manager.create_tables()

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
    def get_user_summeries(self, steamids):
        result = {}

        # Identify which steamids are not in the cache
        not_cached_steamids = [steamid for steamid in steamids if steamid not in self.db_manager.fetch_user(steamid)]
        if not_cached_steamids:
            # Make one request for all not cached steamids
            response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.STEAM_KEY}&steamids={','.join(not_cached_steamids)}")
            data = response.json()
            self.db_manager.insert_user_summary(data)
                
        # Retrieve data from cache for all steamids
        for steamid in steamids:
            result[steamid] = self.db_manager.fetch_user(steamid)
        print(result)
        return result

    def get_user_friend_list(self, steamid):
        friend_ids = self.db_manager.fetch_friends(steamid)
        if friend_ids == []:
            response = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={self.STEAM_KEY}&steamid={steamid}&relationship=friend")
            if not "friendslist" in response.json():
                print(response.json(), "Error getting friends data")
                return False
            friend_ids = [i['steamid'] for i in response.json()["friendslist"]["friends"]]
            self.db_manager.insert_friend_list(steamid, friend_ids)
            
        data = self.get_user_summeries(friend_ids)
        return data

    def get_user_achievements_per_game(self, steamid, appid):
        achievements = self.db_achievements.fetch_user_achievements(steamid, appid)
        if achievements == []:
            response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
            data = response.json()
            try:
                self.db_achievements.insert_achievements(steamid, appid, data)
            except KeyError:
                return "Profile is not public"
            achievements = self.db_achievements.fetch_user_achievements(steamid, appid)
            return achievements
        return achievements

    def get_user_stats_for_game(self, steamid ,appid):
        stats_for_game = self.db_achievements.fetch_user_achieved_achievements(steamid, appid)
        if stats_for_game != []:
            # this api call may no longer be necessary as data is similar to user achievements beside not displaying
            # unlock time, some name changes, and some other information that I can leave out from a fetch call
            #response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
            #data = response.json()
            self.get_user_achievements_per_game(steamid, appid)
            stats_for_game = self.db_achievements.fetch_user_achieved_achievements(steamid, appid)
            return stats_for_game
        return stats_for_game

    def get_user_owned_games(self, steamid):
        games = self.db_manager.fetch_games(steamid)
        if games == []:
            response = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&include_appinfo=true&format=json")
            data = response.json()['response']
            self.db_manager.insert_user_owned_games(steamid, data)
            games = self.db_manager.fetch_games(steamid)
            return games
        else:
            return games

    def get_user_recently_played(self, steamid,count):
        # Implement cache
        # Will not implement databasing here
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&count={count}&format=json")
        # corrected code possibly needs review
        data = response.json()['response']
        return data
        # return response.json()["friendslist"]

    def get_global_achievement_percentage(self, appid):
        if appid in self.cache['game_global_achievement']:
            return self.cache['game_global_achievement'][appid]
        
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}&format=json")
        data = response.json()
        self.cache['game_global_achievement'][appid] = data
        print(data)
        return data
    
    def resolve_vanity_url(self, vanityurl):
        vanityurl = str(vanityurl).replace("https://steamcommunity.com/id/", "").replace("/", "")
        response = requests.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={self.STEAM_KEY}&vanityurl={vanityurl}")
        return response.json()["response"]

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

        print(result)
        return result

    def get_app_news(self, appid,count=3,maxlength=300):
        if appid in self.cache['app_news']:
            return self.cache['app_news'][appid]
        
        response = requests.get(f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count={count}&maxlength={maxlength}&format=json")
        # data = response.json()['response']
        data = response.json()
        self.cache['app_news'][appid] = data
        return data

    def get_user_inventory(self, steamid):
        # if appid in self.cache['user_inventory']:
        #     return self.cache['user_inventory'][steamid]
        
        response = requests.get(f"https://steamcommunity.com/inventory/{steamid}/440/2")
        data = response.json()
        #data = response.json()['response']
        self.cache['user_inventory'][steamid] = data
        print(data)
        return data

    def get_user_group_list(self, steamid):
        if steamid in self.cache['user_groups']:
            return self.cache['user_groups'][steamid]
        
        response = requests.get(f"https://api.steampowered.com/ISteamUser/GetUserGroupList/v1?steamid={steamid}&key={self.STEAM_KEY}")
        data = response.json()['response']
        self.cache['user_groups'][steamid] = data
        return data
    
    def get_number_of_players_in_game(self, appid):
        response = requests.get(f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1?appid={appid}")
        data = response.json()['response']
        return data

    def get_user_steam_level(self, steamid):
        if steamid in self.cache['user_level']:
            print(self.cache['user_level'][steamid])
            return self.cache['user_level'][steamid]
        
        response = requests.get(f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1?steamid={steamid}&key={self.STEAM_KEY}")
        data = response.json()['response']
        self.cache['user_level'][steamid] = data
        print(data)
        return data
    
    def get_user_badges(self, steamid):
        if steamid in self.cache['user_badges']:
            return self.cache['user_badges'][steamid]
        
        response = requests.get(f"https://api.steampowered.com/IPlayerService/GetBadges/v1?steamid={steamid}&key={self.STEAM_KEY}")
        data = response.json()['response']
        self.cache['user_badges'][steamid] = data
        return data

    def clear_cache(self):
        for cache_key in self.cache:
            self.cache[cache_key] = {}
            
            
