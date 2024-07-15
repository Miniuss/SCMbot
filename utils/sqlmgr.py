import sqlite3
from os.path import join as path_join
from os.path import exists as path_exists

class DatabaseManager():
    def __init__(self, dbpath: str):
        path = path_join(*dbpath.split("/"))
        already_written = path_exists(path)

        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        
        if not already_written:
            self._db_notfound_protocol()

    def _db_notfound_protocol(self):
        self.cursor.execute(
            """
            CREATE TABLE forms(
                form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INT NOT NULL UNIQUE,
                upload_time INT NOT NULL,
                steam_profile_url TEXT NOT NULL,
                steam_content_url TEXT NOT NULL,
                claimed_roles TEXT,
                approver_uid INT
            )
            """
        )
        self.connection.commit()

    def write_form_data(
            self, uid: int, upload_time: int, 
            steam_profile_url: str, steam_content_url: str,
            claimed_roles: str = None):
        
        query = """ INSERT INTO forms(
                        uid, 
                        upload_time, 
                        steam_profile_url, 
                        steam_content_url, 
                        claimed_roles
                    )
                    VALUES(?, ?, ?, ?, ?) """

        params = (uid, upload_time, steam_profile_url, steam_content_url, claimed_roles)

        self.cursor.execute(query, params)
        self.connection.commit()

    def role_approval(self, form_id: int, approver_uid: int):
        query = """ UPDATE forms SET approver_uid = ? WHERE form_id = ? """
        params = (form_id, approver_uid)

        self.cursor.execute(query, params)
        self.connection.commit()

    def remove_record(self, form_id: int = -1, uid: int = -1):
        query = """ DELETE FROM forms WHERE form_id = ? OR uid = ? """
        params = (form_id, uid)

        self.connection.commit()

    def exctract_record_data(self, form_id: int = -1, uid: int = -1):
        query = """ SELECT * FROM forms WHERE form_id = ? OR uid = ? """
        params = (form_id, uid)

        data = self.cursor.execute(query, params)
        data = data.fetchone()

        if data is None:
            return None

        key_names = ("id", "uid", "upload_time", 
                     "steam_profile_url", "steam_content_url", 
                     "claimed_roles", "approver_uid")
        
        return dict(zip(key_names, data))
