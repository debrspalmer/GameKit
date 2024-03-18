import sqlite3

class DatabaseManager:
    def __init__(self, database):
        self.database = database
        self.cache = {
            'user_summaries': {},
            'friends': {},
            'user_games': {}
            }

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                friend_steamid TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
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
                rtime_last_played INTEGER,
                content_descriptorids TEXT,
                playtime_disconnected INTEGER
            )
        ''')

        conn.commit()
        conn.close()
     
    def create_achievements_table(self, gameName):
        
        gameName = gameName.replace(" ", "_").replace("'", "").replace('"', '')

        # Create the SQL query to create the achievements table
        query = '''
            CREATE TABLE IF NOT EXISTS "{}_achievements" (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INT,
                gameName TEXT,
                apiname TEXT,
                achieved INTEGER,
                unlocktime INTEGER
            )
        '''.format(gameName)

        # Execute the SQL query
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
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
    # Insert user summary data into the database
        for data in reponse["response"]["players"]:
            steamid = data['steamid']
            existing_user = self.fetch_user(steamid)
            if existing_user != []:
                pass
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
                    INSERT INTO users (
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
                self.cache['user_summaries'].pop('SELECT * FROM users', None)

    def fetch_user(self, steamid):
        if steamid in self.cache['user_summaries']:
            return self.cache['user_summaries'][steamid]

        query = "SELECT * FROM users WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row  # Set row factory to return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        result = cursor.fetchone()
        conn.close()

        if result:
            result = dict(result)  # Convert the row to a dictionary
            self.cache['user_summaries'][steamid] = result  # Cache the result with steamid as key
            return [result]  # Wrap the result in a list
        else:
            return []  # Return an empty list if no results are found
        
    def insert_friend_list(self, steamid, friends):
        if friends == self.fetch_friends(steamid):
            pass
        else:
            query = 'INSERT INTO friends (steamid, friend_steamid) VALUES (?, ?)'
            for friend in friends:
                self.execute_query(query, (steamid, friend))
    
    def fetch_friends(self, steamid):
        if steamid in self.cache['friends']:
            return self.cache['friends'][steamid]

        query = "SELECT friend_steamid FROM friends WHERE steamid = ?"
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
        existing_games = self.fetch_games(steamid)
        if existing_games == games:
            return  # Games for this user already exist in the database

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
                game['rtime_last_played'] if 'rtime_last_played' in game else 0,
                ','.join(str(desc) for desc in game['content_descriptorids']) if 'content_descriptorids' in game else '',
                game['playtime_disconnected'] if 'playtime_disconnected' in game else 0
            ]

            query = '''
                INSERT INTO games (
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
                    rtime_last_played,
                    content_descriptorids,
                    playtime_disconnected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.execute_query(query, values)
                
    def fetch_games(self, steamid):
        if steamid in self.cache['user_games']:
            return self.cache['user_games'][steamid]

        query = "SELECT * FROM games WHERE steamid = ?"
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
                game.pop('id')
                game.pop('steamid')
                games_data.append(game)

            self.cache['user_games'][steamid] = {'game_count': len(games_data), 'games': games_data}
            return self.cache['user_games'][steamid]
        else:
            return []

    def insert_achievements(self, steamid, appid, achievements):
        # Create the achievements table if it doesn't exist
        gameName = achievements['playerstats']['gameName']
        self.create_achievements_table(gameName)

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        # Insert achievements into the dynamic table
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
            '''.format(gameName.replace(" ", "_").replace("'", "").replace('"', ''))

            cursor.execute(query, values)

        conn.commit()
        conn.close()
        
    def fetch_user_achievements(self, steamid, gameName):
        # Construct cache key
        cache_key = f"{steamid}_{gameName}"

        # Check if data exists in cache
        if 'user_achievements' in self.cache and cache_key in self.cache['user_achievements']:
            return self.cache['user_achievements'][cache_key]

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        query = '''
            SELECT apiname, achieved, unlocktime
            FROM "{}_achievements"
            WHERE steamid = ? AND gameName = ?
        '''.format(gameName.replace(" ", "_").replace("'", "").replace('"', ''))

        cursor.execute(query, (steamid, gameName))
        rows = cursor.fetchall()

        achievements = []
        for row in rows:
            achievement = {
                'apiname': row[0],
                'achieved': row[1],
                'unlocktime': row[2]
            }
            achievements.append(achievement)

        conn.close()

        # Store data in user_achievements cache
        if 'user_achievements' not in self.cache:
            self.cache['user_achievements'] = {}

        if achievements:
            self.cache['user_achievements'][cache_key] = {
                'playerstats': {
                    'steamID': steamid,
                    'gameName': gameName,
                    'achievements': achievements
                },
                'success': True
            }
        else:
            # If no data found, return an empty list
            return []

        return self.cache['user_achievements'][cache_key]