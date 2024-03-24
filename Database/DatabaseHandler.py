import sqlite3

class DatabaseManager:
    def __init__(self, database):
        self.database = database
        self.cache = {
            'user_summaries': {},
            'friends': {},
            'user_games': {},
            'user_achievements': {},
            'user_achieved_achievements': {},
            'recently_played': {},
            'user_groups': {},
            'game_global_achievement': {},
            'user_level': {}
            }

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                steamid TEXT PRIMARY KEY,
                communityvisibilitystate INTEGER,
                profilestate INTEGER,
                personaname TEXT,
                commentpermission INTEGER,
                profileurl TEXT,
                avatar TEXT,
                avatarmedium TEXT,
                avatarfull TEXT,
                avatarhash TEXT,
                lastlogoff INTEGER,
                personastate INTEGER,
                realname TEXT,
                primaryclanid TEXT,
                timecreated INTEGER,
                personastateflags INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Friends (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                friend_steamid TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserGames (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                name TEXT,
                playtime_2weeks INTEGER,
                playtime_forever INTEGER,
                img_icon_url TEXT,
                has_community_visible_stats BOOLEAN,
                playtime_windows_forever INTEGER,
                playtime_mac_forever INTEGER,
                playtime_linux_forever INTEGER,
                playtime_deck_forever INTEGER,
                rtime_last_played INTEGER,
                has_leaderboards BOOLEAN,
                content_descriptorids TEXT,
                playtime_disconnected INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserGroups (
                steamid TEXT,
                gid TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserLevel (
                steamid TEXT PRIMARY KEY,
                player_level INTEGER
            )
        ''')

        conn.commit()
        conn.close()
     
    def create_achievements_table(self, appid):
        
        appid = appid.replace(" ", "_").replace("'", "").replace('"', '')

        # Create the SQL query to create the achievements table
        query = '''
            CREATE TABLE IF NOT EXISTS "{}_achievements" (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                gameName TEXT,
                apiname TEXT,
                achieved INTEGER,
                unlocktime INTEGER
            )
        '''.format(appid)

        # Execute the SQL query
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute(query)
        
        query = '''
            CREATE TABLE IF NOT EXISTS AchievementPercentages (
                id INTEGER PRIMARY KEY,
                appid INTEGER,
                name TEXT,
                percent REAL
            )
        '''
        
        cursor.execute(query)
        conn.commit()
        conn.close()
           
    def execute_query(self, query, params=None, fetchone=False):
        # Execute query and cache the result if needed
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        if params:
            # Use the query and parameters as the cache key
            cache_key = (query, tuple(params))
        else:
            cache_key = query

        if cache_key in self.cache:
            result = self.cache[cache_key]
        else:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            self.cache[cache_key] = result

        conn.commit()
        conn.close()

        return result

    def insert_user_summary(self, reponse):
        for data in reponse["response"]["players"]:
            steamid = data['steamid']
            existing_user = self.fetch_user(steamid)
            if existing_user != []:
                return
            else:
                values = [
                    data['steamid'],
                    data['communityvisibilitystate'] if 'communityvisibilitystate' in data else '',
                    data['profilestate'] if 'profilestate' in data else '',
                    data['personaname'] if 'personaname' in data else '',
                    data['commentpermission'] if 'commentpermission' in data else '',
                    data['profileurl'] if 'profileurl' in data else '',
                    data['avatar'] if 'avatar' in data else '',
                    data['avatarmedium'] if 'avatarmedium' in data else '',
                    data['avatarfull'] if 'avatarfull' in data else '',
                    data['avatarhash'] if 'avatarhash' in data else '',
                    data['lastlogoff'] if 'lastlogoff' in data else '',
                    data['personastate'] if 'personastate' in data else '',
                    data['realname'] if 'realname' in data else '',
                    data['primaryclanid'] if 'primaryclanid' in data else '',
                    data['timecreated'] if 'timecreated' in data else '',
                    data['personastateflags'] if 'personastateflags' in data else ''
                ]

                # Insert user summary data into the database
                query = '''
                    INSERT INTO Users (
                        steamid,  
                        communityvisibilitystate, 
                        profilestate, 
                        personaname,
                        commentpermission, 
                        profileurl, 
                        avatar, 
                        avatarmedium, 
                        avatarfull, 
                        avatarhash, 
                        lastlogoff, 
                        personastate, 
                        realname,
                        primaryclanid, 
                        timecreated, 
                        personastateflags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                self.execute_query(query, values)

                # Invalidate cache for users table
                self.cache['user_summaries'].pop('SELECT * FROM Users', None)

    def fetch_user(self, steamid):
        if steamid in self.cache['user_summaries']:
            return self.cache['user_summaries'][steamid]

        query = "SELECT * FROM Users WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        result = cursor.fetchone()
        conn.close()

        if result:
            result = dict(result)
            self.cache['user_summaries'][steamid] = result
            return result
        else:
            return []
        
    def insert_friend_list(self, steamid, friends):
        existing_friends = self.fetch_friends(steamid)
        if existing_friends != []:
            return
        else:
            query = 'INSERT INTO Friends (steamid, friend_steamid) VALUES (?, ?)'
            for friend in friends:
                self.execute_query(query, (steamid, friend))
    
    def fetch_friends(self, steamid):
        if steamid in self.cache['friends']:
            return self.cache['friends'][steamid]

        query = "SELECT friend_steamid FROM Friends WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        results = cursor.fetchall()
        conn.close()
        if results:
            friends = [result[0] for result in results]  # Extract friend steamids from the results
            self.cache['friends'][steamid] = friends  # Cache the results
            return friends
        else:
            return []

    def insert_user_owned_games(self, steamid, games):
        existing_games = self.fetch_user_owned_games(steamid)
        if existing_games != []:
            return
        for game in games['games']:
            values = [
                steamid,
                game['appid'],
                game['name'],
                game['playtime_2weeks'] if 'playtime_2weeks' in game else 0,
                game['playtime_forever'] if 'playtime_forever' in game else 0,
                game['img_icon_url'],
                game['has_community_visible_stats'] if 'has_community_visible_stats' in game else False,
                game['playtime_windows_forever'] if 'playtime_windows_forever' in game else 0,
                game['playtime_mac_forever'] if 'playtime_mac_forever' in game else 0,
                game['playtime_linux_forever'] if 'playtime_linux_forever' in game else 0,
                game['playtime_deck_forever'] if 'playtime_deck_forever' in game else 0, 
                game['rtime_last_played'] if 'rtime_last_played' in game else 0,
                game['has_leaderboards'] if 'has_leaderboards' in game else False,
                ','.join(str(desc) for desc in game['content_descriptorids']) if 'content_descriptorids' in game else '',
                game['playtime_disconnected'] if 'playtime_disconnected' in game else 0
            ]

            query = '''
                INSERT INTO UserGames (
                    steamid,
                    appid,
                    name,
                    playtime_2weeks,
                    playtime_forever,
                    img_icon_url,
                    has_community_visible_stats,
                    playtime_windows_forever,
                    playtime_mac_forever,
                    playtime_linux_forever,
                    playtime_deck_forever,
                    rtime_last_played,
                    has_leaderboards,
                    content_descriptorids,
                    playtime_disconnected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.execute_query(query, values)
                
    def fetch_user_owned_games(self, steamid):
        if steamid in self.cache['user_games']:
            return self.cache['user_games'][steamid]

        query = "SELECT * FROM UserGames WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row  # Set row factory to return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        result = cursor.fetchall()
        conn.close()

        games_data = []
        if result:
            for row in result:
                game = dict(row)
                if game.get('content_descriptorids') == '':
                    game.pop('content_descriptorids')
                else:   
                    content_descrip = game.get('content_descriptorids')
                    integer_list = [int(x) for x in content_descrip.split(',')]
                    game.update({'content_descriptorids': integer_list})
                
                if game.get('playtime_2weeks') == 0:
                    game.pop('playtime_2weeks')
                
                if game.get('has_community_visible_stats') == 0:
                    game.pop('has_community_visible_stats')
                else:
                    game.update({'has_community_visible_stats': True})
                
                if game.get('has_leaderboards') == 0:
                    game.pop('has_leaderboards')
                else:
                    game.update({'has_leaderboards': True})
                
                game.pop('id')
                game.pop('steamid')
                games_data.append(game)

            self.cache['user_games'][steamid] = {'game_count': len(games_data), 'games': games_data}
            return self.cache['user_games'][steamid]
        else:
            return []

    def fetch_recently_played_games(self, steamid, count):
        if steamid in self.cache['recently_played']:
            return self.cache['recently_played'][steamid]

        query = "SELECT * FROM UserGames WHERE steamid = ? AND playtime_2weeks != 0 ORDER BY playtime_2weeks DESC"
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row  # Set row factory to return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        result = cursor.fetchall()
        conn.close()

        games_data = []
        if result:
            for i, row in enumerate(result):
                if i >= count or not row:
                    break
                game = dict(row)
                game.pop('playtime_linux_forever')
                game.pop('playtime_deck_forever')
                game.pop('rtime_last_played')
                game.pop('playtime_disconnected')
                game.pop('playtime_mac_forever')
                game.pop('playtime_windows_forever')
                game.pop('has_community_visible_stats')
                game.pop('content_descriptorids')
                game.pop('has_leaderboards')
                game.pop('id')
                game.pop('steamid')
                games_data.append(game)

            self.cache['recently_played'][steamid] = {'total_count': len(games_data), 'games': games_data}
            return self.cache['recently_played'][steamid]
        else:
            return []
        
    def insert_global_achievements(self, appid, achievements):
        existing_achievements = self.fetch_achievement_percentages(appid)
        if existing_achievements != []:
            return
        else:
            for achievement in achievements['achievementpercentages']['achievements']:
                name = achievement['name']
                percent = achievement['percent']
                values = [appid, name, percent]
                query = '''
                    INSERT INTO AchievementPercentages (appid, name, percent)
                    VALUES (?, ?, ?)
                '''
                self.execute_query(query, values)
        
    def fetch_achievement_percentages(self, appid):
        if appid in self.cache['game_global_achievement']:
            return self.cache['game_global_achievement'][appid]
        else:
            query = '''
                SELECT name, percent FROM AchievementPercentages WHERE appid = ?
            '''
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute(query, (appid,))
            results = cursor.fetchall()
            conn.close()
            if results:
                achievements = [{'name': result[0], 'percent': result[1]} for result in results]
                self.cache['game_global_achievement'][appid] = {'achievementpercentages': {'achievements': achievements}}
                return self.cache['game_global_achievement'][appid]
            else:
                return []
        
    def insert_achievements(self, steamid, appid, achievements):
        gameName = achievements['playerstats']['gameName']
        string_appid = str(appid)
        existing_user = self.fetch_user_achievements(steamid, string_appid)
        if existing_user != []:
            return
        else:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            for achievement in achievements['playerstats']['achievements']:
                values = [
                    steamid,
                    appid,
                    gameName,
                    achievement['apiname'],
                    achievement['achieved'],
                    achievement['unlocktime']
                ]
                query = '''
                    INSERT OR REPLACE INTO "{}_achievements" (
                        steamid,
                        appid,
                        gameName,
                        apiname,
                        achieved,
                        unlocktime
                    ) VALUES (?, ?, ?, ?, ?, ?)
                '''.format(string_appid.replace(" ", "_").replace("'", "").replace('"', ''))

                cursor.execute(query, values)

            conn.commit()
            conn.close()
        
    def fetch_user_achievements(self, steamid, appid):
        string_appid = str(appid)
        cache_key = f"{steamid}_{string_appid}"
        
        if 'user_achievements' in self.cache and cache_key in self.cache['user_achievements']:
            return self.cache['user_achievements'][cache_key]

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (f"{string_appid}_achievements",))
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            conn.close()
            return []
        query = '''
            SELECT gameName, apiname, achieved, unlocktime
            FROM "{}_achievements"
            WHERE steamid = ? AND appid = ?
        '''.format(string_appid.replace(" ", "_").replace("'", "").replace('"', ''))

        cursor.execute(query, (steamid, string_appid))
        rows = cursor.fetchall()

        achievements = []
        gameName = None
        for row in rows:
            gameName = row[0]
            achievement = {
                'apiname': row[1],
                'achieved': row[2],
                'unlocktime': row[3]
            }
            achievements.append(achievement)

        conn.close()
        if 'user_achievements' not in self.cache:
            self.cache['user_achievements'] = {}

        if achievements:
            self.cache['user_achievements'][cache_key] = {
                'playerstats': {
                    'steamID': steamid,
                    'gameName': gameName,
                    'achievements': achievements,
                    'success': True
                }
            }
        else:
            return []

        return self.cache['user_achievements'][cache_key]
    
    def fetch_user_achieved_achievements(self, steamid, appid):
        string_appid = str(appid)
        cache_key = f"{steamid}_{string_appid}"

        if cache_key in self.cache['user_achieved_achievements']:
            return self.cache['user_achieved_achievements'][cache_key]

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (f"{string_appid}_achievements",))
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            conn.close()
            return []

        query = '''
            SELECT apiname, achieved
            FROM "{}_achievements"
            WHERE steamid == ? AND appid == ? AND achieved == 1
        '''.format(string_appid.replace(" ", "_").replace("'", "").replace('"', ''))

        cursor.execute(query, (steamid, string_appid))
        rows = cursor.fetchall()

        achievements = []
        gameName = None  # Initialize gameName to None
        for row in rows:
            achievement = {
                'name': row[0], 
                'achieved': row[1]
            }
            achievements.append(achievement)

            if gameName is None:
                gameName_query = '''
                    SELECT gameName
                    FROM "{}_achievements"
                    WHERE apiname == ? AND steamid == ? AND appid == ?
                    LIMIT 1
                '''.format(string_appid.replace(" ", "_").replace("'", "").replace('"', ''))
                cursor.execute(gameName_query, (row[0], steamid, string_appid))
                gameName_row = cursor.fetchone()
                if gameName_row:
                    gameName = gameName_row[0]

        conn.close()

        result = {
            'playerstats': {
                'steamID': steamid,
                'gameName': gameName,
                'achievements': achievements
            }
        }

        if 'user_achieved_achievements' not in self.cache:
            self.cache['user_achieved_achievements'] = {}

        self.cache['user_achieved_achievements'][cache_key] = result

        formatted_result = {
            'playerstats': {
                'steamID': result['playerstats']['steamID'],
                'gameName': result['playerstats']['gameName'],
                'achievements': [{'name': achievement['name'], 'achieved': achievement['achieved']} for achievement in result['playerstats']['achievements'] if achievement['achieved'] == 1]
            }
        }

        return formatted_result
    
    def insert_user_groups(self, steamid, groups):
        existing_group = self.fetch_user_groups(steamid)
        if existing_group != []:
            return
        
        for group in groups['groups']:
            values = [
                steamid,
                group['gid']
            ]
        
            query = '''
                INSERT INTO UserGroups (
                    steamid,
                    gid
                ) VALUES (?, ?)
            '''
            self.execute_query(query, values)
        
    def fetch_user_groups(self, steamid):
        if steamid in self.cache['user_groups']:
            return self.cache['user_groups'][steamid]
        
        query = "SELECT gid FROM UserGroups WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        results = cursor.fetchall()
        conn.close()
        if results:
            group_ids = [result[0] for result in results]
            groups = {'success': True, 'groups': [{'gid': gid} for gid in group_ids]}
            self.cache['user_groups'][steamid] = groups
            return groups
        else:
            return []
        
    def insert_user_level(self, steamid, data):
        existing_level = self.fetch_user_groups(steamid)
        if existing_level != []:
            return
        
        values = [
            steamid, 
            data['player_level']
            ]
        
        query = '''
                INSERT INTO UserLevel (
                    steamid,
                    player_level
                ) VALUES (?, ?)
            '''
        self.execute_query(query, values)
        
    def fetch_user_level(self, steamid):
        if steamid in self.cache['user_level']:
            return self.cache['user_level'][steamid]
        
        query = "SELECT player_level FROM UserLevel WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        results = cursor.fetchall()
        conn.close()
        
        if results:
            level = [result[0] for result in results]
            level = level[0]
            self.cache['user_level'][steamid] = {'player_level': level}
            return self.cache['user_level'][steamid]
        else:
            return []
# Add method to clear table in its entirety 