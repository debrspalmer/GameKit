import requests

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
        }

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
        
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&format=json")
        data = response.json()
        self.cache['user_owned_games'][steamid] = data
        return data
    def get_user_recently_played(self, steamid,count):
        # Implement cache
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&count={count}&format=json")
        return response.json()["friendslist"]

    def clear_cache(self):
        for cache_key in self.cache:
            self.cache[cache_key] = {}
