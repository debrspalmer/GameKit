import requests
class Steam:
    STEAM_KEY='xxxxxxxxxxxxx'
    def __init__(self, key):
        self.STEAM_KEY=key
    def get_user_steamid(self, username):
        pass
    def get_user_friend_list(self, steamid):
        response = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={self.STEAM_KEY}&steamid={steamid}&relationship=friend")
        return response.json()
    def get_user_achievements(self, steamid,appid):
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
        return response.json()
    def get_user_stats_for_game(self, steamid,appid):
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={self.STEAM_KEY}&steamid={steamid}")
        return response.json()
    def get_user_owned_games(self, steamid):
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&format=json")
        return response.json()
    def get_user_recently_played(self, steamid,count):
        response = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.STEAM_KEY}&steamid={steamid}&count={count}&format=json")
        return response.json()["friendslist"]