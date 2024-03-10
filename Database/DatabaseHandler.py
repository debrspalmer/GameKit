import sqlite3

class DatabaseManager:
    def __init__(self, database):
        self.database = database
        self.cache = {}

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
                friend_username TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                name TEXT,
                playtime INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                achievements_data TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                stats_data TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_recently_played (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                appid INTEGER,
                playtime INTEGER,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_global_achievement (
                id INTEGER PRIMARY KEY,
                appid INTEGER,
                achievement_percentage REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_details (
                id INTEGER PRIMARY KEY,
                appid INTEGER,
                app_details_data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inventory (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                inventory_data TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                steamid TEXT NOT NULL,
                group_id TEXT NOT NULL,
                group_name TEXT NOT NULL,
                group_url TEXT NOT NULL,
                group_avatar TEXT,
                group_description TEXT,
                group_member_count INTEGER,
                group_visibility TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_level (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                level INTEGER,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY,
                steamid TEXT,
                badges_data TEXT,
                FOREIGN KEY (steamid) REFERENCES users(steamid)
            )
        ''')

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
                self.cache.pop('SELECT * FROM users', None)

    def fetch_user(self, steamid):
        if steamid in self.cache:
            return self.cache[steamid]

        query = "SELECT * FROM users WHERE steamid = ?"
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row  # Set row factory to return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(query, (steamid,))
        result = cursor.fetchone()
        conn.close()

        if result:
            result = dict(result)  # Convert the row to a dictionary
            self.cache[steamid] = result  # Cache the result with steamid as key
            return [result]  # Wrap the result in a list
        else:
            return []  # Return an empty list if no results are found
        
    # def insert_friend_list(steamid, friends):
        # query = 'SELECT COUNT(*) FROM friends WHERE steamid = ?'
        # existing_friends_count = execute_query(query, (steamid,), fetchone=True, cache=friends_cache)[0]

        # if existing_friends_count == 0:
        #     for friend in friends:
        #         query = 'INSERT INTO friends (steamid, friend_steamid, friend_username) VALUES (?, ?, ?)'
        #         execute_query(query, (steamid, friend['steamid'], friend['personaname']))
    
# def insert_user_owned_games(steamid, games):
#     query = 'SELECT COUNT(*) FROM games WHERE steamid = ?'
#     existing_games_count = execute_query(query, (steamid,), fetchone=True, cache=games_cache)[0]

#     if existing_games_count == 0:
#         for game in games:
#             query = 'INSERT INTO games (steamid, appid, name, playtime) VALUES (?, ?, ?, ?)'
#             execute_query(query, (steamid, game['appid'], game['name'], game.get('playtime_forever', 0)), cache=games_cache)


# def insert_user_achievements(steamid, appid, achievements_data):
#     query = 'SELECT COUNT(*) FROM user_achievements WHERE steamid = ? AND appid = ?'
#     existing_achievements_count = execute_query(query, (steamid, appid), fetchone=True, cache=achievements_cache)[0]

#     if existing_achievements_count == 0:
#         query = 'INSERT INTO user_achievements (steamid, appid, achievements_data) VALUES (?, ?, ?)'
#         execute_query(query, (steamid, appid, achievements_data), cache=achievements_cache)

# def insert_user_stats(steamid, appid, stats_data):
#     query = 'SELECT COUNT(*) FROM user_stats WHERE steamid = ? AND appid = ?'
#     existing_stats_count = execute_query(query, (steamid, appid), fetchone=True, cache=stats_cache)[0]

#     if existing_stats_count == 0:
#         query = 'INSERT INTO user_stats (steamid, appid, stats_data) VALUES (?, ?, ?)'
#         execute_query(query, (steamid, appid, stats_data), cache=stats_cache)

# def insert_user_recently_played(steamid, appid, playtime):
#     query = 'SELECT COUNT(*) FROM user_recently_played WHERE steamid = ? AND appid = ?'
#     existing_recently_played_count = execute_query(query, (steamid, appid), fetchone=True, cache=recently_played_cache)[0]

#     if existing_recently_played_count == 0:
#         query = 'INSERT INTO user_recently_played (steamid, appid, playtime) VALUES (?, ?, ?)'
#         execute_query(query, (steamid, appid, playtime), cache=recently_played_cache)

# def insert_game_global_achievement(appid, achievement_percentage):
#     query = 'SELECT COUNT(*) FROM game_global_achievement WHERE appid = ?'
#     existing_global_achievement_count = execute_query(query, (appid,), fetchone=True, cache=global_achievement_cache)[0]

#     if existing_global_achievement_count == 0:
#         query = 'INSERT INTO game_global_achievement (appid, achievement_percentage) VALUES (?, ?)'
#         execute_query(query, (appid, achievement_percentage), cache=global_achievement_cache)

# def insert_app_details(appid, app_details_data):
#     query = 'SELECT COUNT(*) FROM app_details WHERE appid = ?'
#     existing_app_details_count = execute_query(query, (appid,), fetchone=True, cache=app_details_cache)[0]

#     if existing_app_details_count == 0:
#         query = 'INSERT INTO app_details (appid, app_details_data) VALUES (?, ?)'
#         execute_query(query, (appid, app_details_data), cache=app_details_cache)

# def insert_user_inventory(steamid, inventory_data):
#     query = 'SELECT COUNT(*) FROM user_inventory WHERE steamid = ?'
#     existing_inventory_count = execute_query(query, (steamid,), fetchone=True, cache=inventory_cache)[0]

#     if existing_inventory_count == 0:
#         query = 'INSERT INTO user_inventory (steamid, inventory_data) VALUES (?, ?)'
#         execute_query(query, (steamid, inventory_data), cache=inventory_cache)

# def insert_user_groups(steamid, group_data):
#     for group_id, group_info in group_data:
#         query = 'SELECT COUNT(*) FROM user_groups WHERE steamid = ? AND group_id = ?'
#         existing_group_count = execute_query(query, (steamid, group_id), fetchone=True, cache=groups_cache)[0]

#         if existing_group_count == 0:
#             query = 'INSERT INTO user_groups (steamid, group_id, group_name, group_url, group_avatar, \
#                 group_description, group_member_count, group_visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
#             execute_query(query, (steamid, group_id, group_info['group_name'], group_info['group_url'], \
#                 group_info['group_avatar'], group_info['group_description'], group_info['group_member_count'], \
#                     group_info['group_visibility']), cache=groups_cache)
    

# def insert_user_level(steamid, level):
#     query = 'SELECT COUNT(*) FROM user_level WHERE steamid = ?'
#     existing_level_count = execute_query(query, (steamid,), fetchone=True, cache=level_cache)[0]

#     if existing_level_count == 0:
#         query = 'INSERT INTO user_level (steamid, level) VALUES (?, ?)'
#         execute_query(query, (steamid, level), cache=level_cache)

# def insert_user_badges(steamid, badges_data):
#     query = 'SELECT COUNT(*) FROM user_badges WHERE steamid = ?'
#     existing_badges_count = execute_query(query, (steamid,), fetchone=True, cache=badges_cache)[0]

#     if existing_badges_count == 0:
#         query = 'INSERT INTO user_badges (steamid, badges_data) VALUES (?, ?)'
#         execute_query(query, (steamid, badges_data), cache=badges_cache)
    
# def fetch_user(steamid):      
#     query = 'SELECT * FROM users WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=users_cache)
#     return result

# def fetch_existing_user_count(steamid):
#     query = 'SELECT COUNT(*) FROM users WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=users_cache)
#     return result[0] if result else 0

# def fetch_existing_friends_count(steamid):
#     query = 'SELECT COUNT(*) FROM friends WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=friends_cache)
#     return result[0] if result else 0

# def fetch_existing_user_achievements_count(steamid, appid):
#     query = 'SELECT COUNT(*) FROM user_achievements WHERE steamid = ? AND appid = ?'
#     result = execute_query(query, (steamid, appid), fetchone=True, cache=achievements_cache)
#     return result[0] if result else 0

# def fetch_existing_user_stats_count(steamid, appid):
#     query = 'SELECT COUNT(*) FROM user_stats WHERE steamid = ? AND appid = ?'
#     result = execute_query(query, (steamid, appid), fetchone=True, cache=stats_cache)
#     return result[0] if result else 0

# def fetch_existing_game_count(steamid):
#     query = 'SELECT COUNT(*) FROM games WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=games_cache)
#     return result[0] if result else 0

# def fetch_existing_recently_played_count(steamid, appid):
#     query = 'SELECT COUNT(*) FROM user_recently_played WHERE steamid = ? AND appid = ?'
#     result = execute_query(query, (steamid, appid), fetchone=True, cache=recently_played_cache)
#     return result[0] if result else 0

# def fetch_existing_global_achievement_count(appid):
#     query = 'SELECT COUNT(*) FROM game_global_achievement WHERE appid = ?'
#     result = execute_query(query, (appid,), fetchone=True, cache=global_achievement_cache)
#     return result[0] if result else 0

# def fetch_existing_app_details_count(appid):
#     query = 'SELECT COUNT(*) FROM app_details WHERE appid = ?'
#     result = execute_query(query, (appid,), fetchone=True, cache=app_details_cache)
#     return result[0] if result else 0

# def fetch_existing_inventory_count(steamid):
#     query = 'SELECT COUNT(*) FROM user_inventory WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=inventory_cache)
#     return result[0] if result else 0

# def fetch_existing_groups_count(steamid):
#     query = 'SELECT COUNT(*) FROM user_groups WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=groups_cache)
#     return result[0] if result else 0

# def fetch_existing_level_count(steamid):
#     query = 'SELECT COUNT(*) FROM user_level WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=level_cache)
#     return result[0] if result else 0

# def fetch_existing_badges_count(steamid):
#     query = 'SELECT COUNT(*) FROM user_badges WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=badges_cache)
#     return result[0] if result else 0

# def fetch_existing_user_count(steamid):
#     query = 'SELECT COUNT(*) FROM users WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=users_cache)
#     return result[0] if result else 0

# def fetch_existing_game_count(steamid):
#     query = 'SELECT COUNT(*) FROM games WHERE steamid = ?'
#     result = execute_query(query, (steamid,), fetchone=True, cache=games_cache)
#     return result[0] if result else 0