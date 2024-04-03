import unittest
import sys
import os
# While I am ware that there is a better way of doing this, i simply dont care enough to do it as it would require reformating the entire application.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SteamHandler import Steam
from unittest.mock import patch, MagicMock, PropertyMock, call

class test_requests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.bad_request_body = """
        <html>
            <head>
                <title>Bad Request</title>
            </head>
            <body>
                <h1>Bad Request</h1>
                Please verify that all required parameters are being sent
            </body>
        </html>
        """
        self.internal_server_error = """
        <html>
            <head>
                <title>Internal Server Error</title>
            </head>
            <body>
                <h1>Internal Server Error</h1>
                Unknown problem determining WebApi request destination.
            </body>
        </html>
        """
    def tearDown(self):
        # This method will run after each test method
        try:
            os.remove('db/database.db')
        except:
            pass
    @patch('SteamHandler.requests.get')
    def test_get_user_summeries(self, mock_get):
        key = "none"
        mock_data = {
            "response": {
                "players": [
                    {
                        "steamid": "76561198180337238",
                        "communityvisibilitystate": 3,
                        "profilestate": 1,
                        "personaname": "buttercheetah",
                        "profileurl": "https://steamcommunity.com/id/buttercheetah/",
                        "avatar": "https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e.jpg",
                        "avatarmedium": "https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e_medium.jpg",
                        "avatarfull": "https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e_full.jpg",
                        "avatarhash": "1fa48f3adeb9594213eb5579244b70f7430ff46e",
                        "lastlogoff": 1707394872,
                        "personastate": 4,
                        "realname": "Noah",
                        "primaryclanid": "103582791460010420",
                        "timecreated": 1424288420,
                        "personastateflags": 0,
                        "loccountrycode": "US",
                        "locstatecode": "NC"
                    }
                ]
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Initialize your class
        steam = Steam(key)

        # Call the method you want to test with a single steamid
        result = steam.get_user_summeries(["76561198180337238"])

        # Assertions
        self.assertIn("76561198180337238", result)  # Check if the steamid is in the result
        user_data = result.get("76561198180337238", {})
        self.assertEqual(user_data["personaname"], "buttercheetah")  # Check specific attribute

        # Verify that requests.get was called with the expected URL
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids=76561198180337238"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_summeries_empty(self, mock_get):
        key = "none"
        mock_data = {"response":{"players":[]}}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Initialize your class
        steam = Steam(key)

        # Call the method you want to test with a single steamid
        result = steam.get_user_summeries(["76561198180337238"])
        # Assertions
        self.assertEqual(result, {'76561198180337238':[]})  # Check if the steamid is in the result
        # Verify that requests.get was called with the expected URL
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids=76561198180337238"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_friend_list_valid_data(self, mock_requests_get):
        # Create an instance of the Steam class with the API key 'xxxx'
        steam = Steam('xxxx')

        # Mock the response from the API with valid data
        mock_response = MagicMock()
        mock_response.json.return_value = {'friendslist': {'friends': [{'steamid': 'friend1'}, {'steamid': 'friend2'}]}}
        mock_requests_get.return_value = mock_response

        # Mock the get_user_summeries method to return a predefined result
        steam.get_user_summeries = MagicMock(return_value={'friend1': {...}, 'friend2': {...}})

        # Call the function with a steamid
        result = steam.get_user_friend_list('test_steamid')

        # Assert that the result is the expected data
        expected_result = {'friend1': {...}, 'friend2': {...}}
        self.assertEqual(result, expected_result)

    @patch('SteamHandler.requests.get')
    def test_get_user_friend_list_empty_list(self, mock_requests_get):
        # Create an instance of the Steam class with the API key 'xxxx'
        steam = Steam('xxxx')

        # Mock the response from the API with an empty friends list
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response

        # Call the function with a steamid
        result = steam.get_user_friend_list('test_steamid')

        # Assert that the result is an empty dictionary
        self.assertEqual(result, False)
    
    @patch('SteamHandler.requests.get')
    def test_get_user_achievements_per_game(self, mock_get):
        key = "none"
        steamid = "76561198180337238"
        appid = "1172470"

        # Set up mock response
        mock_data = {
            "playerstats":{
                "steamID":"76561198180337238",
                "gameName":"Apex Legends",
                "achievements":[
                    {"apiname":"THE_PLAYER_0","achieved":1,"unlocktime":1605558532},
                    {"apiname":"DECKED_OUT_1","achieved":1,"unlocktime":1605822181}],
                    "success":True
                }
            }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_user_achievements_per_game(steamid, appid)

        # Assertions (Checking for game name and steam id)
        #self.assertEqual(result["playerstats"]["steamID"], steamid)
        #self.assertEqual(result["playerstats"]["gameName"], "Apex Legends")
        #self.assertEqual(result["playerstats"]["success"], True)

        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}"
        )
    
    @patch('SteamHandler.requests.get')
    def test_get_user_achievements_per_game_none(self, mock_get):
        key = "none"
        steamid = "76561198180337238"
        appid = "1172470"

        # Set up mock response
        mock_data = {"playerstats":{"error":"Requested app has no stats","success":False}}
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_user_achievements_per_game(steamid, appid)

        # Assertions (Checking for game name and steam id)
        self.assertEqual(result, [])
        self.assertIsNotNone(result)

        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}"
        )
    
    @patch('SteamHandler.requests.get')
    def test_get_user_stats(self, mock_get):
        key="none"
        steamid="76561198180337238"
        appid="1172470"

        mock_data = {
            "playerstats":{
                "steamID":"76561198180337238",
                "gameName":"Telstar_APL",
                "achievements":[
                    {"name":"THE_PLAYER_0","achieved":1},
                    {"name":"DECKED_OUT_1","achieved":1}
                    ]
                }
            }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_user_stats_for_game(steamid, appid)
        print('umm',result)
        # Assertions (Not checking Every achievement)
        #self.assertEqual(result["playerstats"]["steamID"], steamid)
        #self.assertEqual(result["playerstats"]["gameName"], "Telstar_APL")
        #self.assertEqual(result["playerstats"]["achievements"][0]["name"], "THE_PLAYER_0")
        #self.assertEqual(result["playerstats"]["achievements"][0]["achieved"], 1)

        mock_get.assert_has_calls(
            [
                call(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={key}&steamid={steamid}"),
                call(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}")
            ],any_order=True
        )

    @patch('SteamHandler.requests.get')
    def test_get_user_stats_none(self, mock_get):
        key="none"
        steamid="76561198180337238"
        appid="1172470"

        # Define your URLs and corresponding data
        urls_data = [
            (f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={key}&steamid={steamid}", {}),
            (f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}", {})
        ]

        mock_data = {}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_user_stats_for_game(steamid, appid)

        # Assertions (Not checking every achievement)
        self.assertEqual(result, [])

        mock_get.assert_has_calls(
            [
                call(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={key}&steamid={steamid}"),
                call(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}")
        ],any_order=True)


    @patch('SteamHandler.requests.get')
    def test_get_user_stats_ise(self, mock_get):
        # Testing outcome if valve returns a internal server error
        key="none"
        steamid="76561198180337238"
        appid="1172470"

        # Define your URLs and corresponding data
        urls_data = [
            (f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={key}&steamid={steamid}", {}),
            (f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}", {})
        ]

        mock_data = self.internal_server_error
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_user_stats_for_game(steamid, appid)

        # Assertions (Not checking every achievement)
        self.assertEqual(result, [])

        mock_get.assert_has_calls(
            [
                call(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={key}&steamid={steamid}"),
                call(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={key}&steamid={steamid}")
        ],any_order=True)

    @patch('SteamHandler.requests.get')
    def test_user_owned_games(self, mock_get):
        key="none"
        steamid="76561198348585939"
        mock_data = {"response":{
            "game_count":2,
            "games":[
                {"appid":1250,"name":"Killing Floor","playtime_forever":1,"img_icon_url":"d8a2d777cb4c59cf06aa244166db232336520547","has_community_visible_stats":True},
                {"appid":35420,"name":"Killing Floor Mod: Defence Alliance 2","playtime_forever":0,"img_icon_url":"ae7580a60cf77b754c723c72d5e31d530fbe7804","has_community_visible_stats":True},
                ]
            }
        }
        mock_response = MagicMock()
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        steam = Steam(key)
        result = steam.get_user_owned_games(steamid)
        self.assertEqual(result["game_count"], 2)
        self.assertEqual(result["games"][0]["name"], "Killing Floor")

        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&include_appinfo=true&format=json"
        )
    @patch('SteamHandler.requests.get')
    def test_user_owned_games_none(self, mock_get):
        key="none"
        steamid="76561198348585939"
        mock_data = self.bad_request_body
        mock_response = MagicMock()
        mock_response.return_value = mock_data
        type(mock_response).status_code = PropertyMock(return_value=400)
        mock_get.return_value = mock_response

        steam = Steam(key)
        result = steam.get_user_owned_games(steamid)
        self.assertEqual(result, [])

        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&include_appinfo=true&format=json"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_recently_played(self, mock_get):
        key="none"
        steamid="76561198180337238"
        count=1
        
        mock_data = {"response":{
            "total_count":1,
            "games":[
                {"appid":553850,"name":"HELLDIVERS™ 2","playtime_2weeks":729,"playtime_forever":729,"img_icon_url":"c3dff088e090f81d6e3d88eabbb67732647c69cf","playtime_windows_forever":729,"playtime_mac_forever":0,"playtime_linux_forever":0}
                ]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)

        result = steam.get_user_recently_played(steamid, count)
        self.assertEqual(result["total_count"], 1)
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&include_appinfo=true&format=json"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_recently_played_none(self, mock_get):
        key="none"
        steamid="76561198180337238"
        count="1"
        
        mock_data = self.bad_request_body

        mock_response = MagicMock()
        mock_response.return_value = mock_data
        type(mock_response).status_code = PropertyMock(return_value=400)
        
        steam = Steam(key)

        result = steam.get_user_recently_played(steamid, count)
        self.assertEqual(result, [])
        mock_get.assert_has_calls(
            [
                call(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&include_appinfo=true&format=json")
        ],any_order=True)
    @patch('SteamHandler.requests.get')
    def test_get_global_achievement_percentage(self, mock_get):
        key="none"
        appid="1172470"
        mock_data = {
            "achievementpercentages":{
                "achievements":[
                    {"name":"JUMPMASTER_4","percent":49.5},
                    {"name":"TEAM_PLAYER_2","percent":42}
                ]
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=400)

        steam = Steam(key)

        result = steam.get_global_achievement_percentage(appid)

        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}&format=json"
        )
    @patch('SteamHandler.requests.get')
    def test_get_global_achievement_percentage_none(self, mock_get):
        key="none"
        appid="1172470"
        mock_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        steam = Steam(key)

        result = steam.get_global_achievement_percentage(appid)

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}&format=json"
        )

    @patch('SteamHandler.requests.get')
    def test_resolve_vanity_url(self, mock_get):
        key="none"
        vanityUrl = "CrekdChase"
        mock_data = {
        "response": {
            "steamid": "76561198250039738",
            "success": 1
        }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)

        steam = Steam(key)

        result = steam.resolve_vanity_url(vanityUrl)
        self.assertEqual(result["success"], 1)
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={key}&vanityurl={vanityUrl}"
        )

    @patch('SteamHandler.requests.get')
    def test_get_app_news(self, mock_get):
        key = "none"
        maxlength = 300
        count = 3
        appid = "1172470"
        mock_data = {
        "appnews": {
            "appid": 1172470,
            "newsitems": [
            {
                "gid": "5686430301718606728",
                "title": "RULE THE UNDERGROUND IN THE SHADOW SOCIETY EVENT",
                "url": "https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/5686430301718606728",
                "is_external_url": "true",
                "author": "respawn_bean",
                "contents": "The underground pauses for no one, Legends. Become...",
                "feedlabel": "Community Announcements",
                "date": 1711041936,
                "feedname": "steam_community_announcements",
                "feed_type": 1,
                "appid": 1172470
            }
            ],
            "count": 1002
        }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)
        result = steam.get_app_news(appid)
        self.assertEqual(result["count"], 1002)
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count={count}&maxlength={maxlength}&format=json"
        )

    @patch('SteamHandler.requests.get')
    def test_get_user_inventory(self, mock_get):
        key = "none"
        id = "76561198250039738"
        mock_data = {
            "assets" : [{"appid" : 440}]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)
        result = steam.get_user_inventory(id,440)
        self.assertIsNotNone(result)
        mock_get.assert_called_once_with(
            f"https://steamcommunity.com/inventory/{id}/440/2"
        )

    @patch('SteamHandler.requests.get')
    def test_get_user_group_list_empty(self, mock_get):
        key ="none"
        id = "76561198250039738"
        mock_data = {
        "response": {
            "success": "true",
            "groups": []
        }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)
        result = steam.get_user_group_list(id)
        print('ehhh',result)
        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            f"https://api.steampowered.com/ISteamUser/GetUserGroupList/v1?steamid={id}&key={key}"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_group_list(self, mock_get):
        key ="none"
        steamid = "76561198250039738"
        mock_data = {
            "response":{
                "success":True,
                "groups":
                    [
                        {"gid":"5134093"},
                        {"gid":"6625556"},
                        {"gid":"6767060"},
                        {"gid":"8067890"},
                        {"gid":"8887082"},
                        {"gid":"8934138"},
                        {"gid":"9164327"},
                        {"gid":"9538146"},
                        {"gid":"25234320"},
                    ]
                }
            
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)
        result = steam.get_user_group_list(steamid)
        print('HELLO!?!?!',result)
        self.assertNotEqual(result, [])
        mock_get.assert_called_once_with(
            f"https://api.steampowered.com/ISteamUser/GetUserGroupList/v1?steamid={steamid}&key={key}"
        )
    @patch('SteamHandler.requests.get')
    def test_get_number_of_players_in_game(self, mock_get):
        key = "none"
        appid = "1172470"
        mock_data = {
        "response": {
            "player_count": 95098,
            "result": 1
        }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=200)
        steam = Steam(key)
        result = steam.get_number_of_players_in_game(appid)
        self.assertEqual(result["player_count"], 95098)
        mock_get.assert_called_once_with(
            f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1?appid={appid}"
        )
    @patch('SteamHandler.requests.get')
    def test_get_user_steam_level(self, mock_get):
        key="none"
        steamid = "76561198250039738"
        

        mock_data = {
                "response": {
                    "player_level": 12
                }
        }
        
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=400)


        steam = Steam(key)
        result = steam.get_user_steam_level(steamid)
        mock_get.assert_called_once_with(
            f"https://api.steampowered.com/IPlayerService/GetBadges/v1?steamid={steamid}&key={key}"
        )

    @patch('SteamHandler.requests.get')
    def test_get_user_badges(self, mock_get):
        key="none"
        steamid = "1172470"
        mock_data = {
        "achievementpercentages": {
            "achievements": [
            {
                "name": "JUMPMASTER_4",
                "percent": 49.4000015258789
            },
            {
                "name": "TEAM_PLAYER_2",
                "percent": 41.9000015258789
            },
            {
                "name": "KILL_LEADER_6",
                "percent": 41.2000007629395
            },
            {
                "name": "FULLY_KITTED_3",
                "percent": 40.0999984741211
            },
            {
                "name": "APEX_RECON_10",
                "percent": 35.7999992370606
            },
            {
                "name": "APEX_OFFENSE_7",
                "percent": 34.7999992370606
            },
            {
                "name": "APEX_SUPPORT_9",
                "percent": 27.7000007629395
            },
            {
                "name": "DECKED_OUT_1",
                "percent": 27.2999992370605
            },
            {
                "name": "THE_PLAYER_0",
                "percent": 24.6000003814697
            },
            {
                "name": "APEX_DEFENSE_8",
                "percent": 20
            },
            {
                "name": "WELL_ROUNDED_5",
                "percent": 16.2999992370605
            },
            {
                "name": "APEX_LEGEND_11",
                "percent": 14.8000001907349
            }
            ]
        }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        type(mock_response).status_code = PropertyMock(return_value=400)
        steam = Steam(key)
        result = steam.get_user_badges(steamid)
        mock_get.assert_called_once_with(
            f"https://api.steampowered.com/IPlayerService/GetBadges/v1?steamid={steamid}&key={key}"
        )
if __name__ == '__main__':

    unittest.main()
