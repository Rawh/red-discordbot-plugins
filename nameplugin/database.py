import sqlite3


class Database():
    def __init__(self, file_name):
        self._file_name = file_name

    def get_all_games(self):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            raw_games_data = cursor.fetchall()
            games = []
            for game in raw_games_data:
                games.append(game[0])
            return games

    def create_game(self, game):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.sanitize_user_input(game)} (id INTEGER PRIMARY KEY, username TEXT, name TEXT, available INTEGER)')

    def clear_game_names(self, game):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {self.sanitize_user_input(game)}')
            connection.commit()

    def get_random_name(self, game):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT name FROM {self.sanitize_user_input(game)} WHERE available=1 ORDER BY RANDOM() LIMIT 1')
            result = cursor.fetchone()
            if result is not None:
                self.make_name_unavailable(game, result[0])
                return result[0]
            else:
                return None

    def get_all_entries(self, game):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {self.sanitize_user_input(game)}')
            data = cursor.fetchall()
            return data

    def user_can_submit(self, game, user_id):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT 1 FROM {self.sanitize_user_input(game)} WHERE id=?', (user_id, ))
            result = cursor.fetchone()
            if result:
                return False
            return True

    def name_exists(self, game, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT 1 FROM {self.sanitize_user_input(game)} WHERE name=? COLLATE NOCASE', (name, ))
            result = cursor.fetchone()
            if result:
                return True
            return False

    def submit_name(self, game, user_id, username, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO {self.sanitize_user_input(game)} VALUES(?, ?, ?, ?)', (user_id, username, name, 1))
            connection.commit()

    def change_name(self, game, user_id, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE {self.sanitize_user_input(game)} SET name=? WHERE id=?', (name, user_id))
            connection.commit()

    def delete_name(self, game, user_id, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {self.sanitize_user_input(game)} WHERE id=?', (user_id, ))
            connection.commit()

    def make_name_available(self, game, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE {self.sanitize_user_input(game)} SET available=? WHERE name=?', (1, name))
            connection.commit()

    def make_name_unavailable(self, game, name):
        with sqlite3.connect(self._file_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE {self.sanitize_user_input(game)} SET available=? WHERE name=?', (0, name))
            connection.commit()

    def sanitize_user_input(self, input_str):
        valid_chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_"]
        sanitized_input = ""
        for char in input_str.lower():
            if char in valid_chars:
                sanitized_input += char
        return sanitized_input
