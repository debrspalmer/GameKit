import unittest
import sys
import os
# While I am ware that there is a better way of doing this, i simply dont care enough to do it as it would require reformating the entire application.
sys.path.append(str(os.getcwd()).replace("/tests", ""))
import SteamHandler
from unittest.mock import patch, MagicMock

class test_requests(unittest.TestCase):

    @patch('SteamHandler.requests.get')  # Mock the requests.get function
    def test_get_user_summeries(self, mock_get):
        key = "none"
        

        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response":{"players":[{"steamid":"76561198180337238","communityvisibilitystate":3,"profilestate":1,"personaname":"buttercheetah","profileurl":"https://steamcommunity.com/id/buttercheetah/","avatar":"https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e.jpg","avatarmedium":"https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e_medium.jpg","avatarfull":"https://avatars.steamstatic.com/1fa48f3adeb9594213eb5579244b70f7430ff46e_full.jpg","avatarhash":"1fa48f3adeb9594213eb5579244b70f7430ff46e","lastlogoff":1707394872,"personastate":4,"realname":"Noah","primaryclanid":"103582791460010420","timecreated":1424288420,"personastateflags":0,"loccountrycode":"US","locstatecode":"NC"}]}}
        mock_get.return_value = mock_response

        # Initialize your class
        Steam = SteamHandler.Steam(key)

        # Call the method you want to test
        result = Steam.get_user_summeries(["76561198180337238"])
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result["76561198180337238"]["personaname"], "buttercheetah")
        
        # Verify that requests.get was called with the expected URL
        mock_get.assert_called_once_with(
            f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={','.join(['76561198180337238'])}"
        )


if __name__ == '__main__':
    unittest.main()
