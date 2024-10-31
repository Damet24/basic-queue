import uuid

import bcrypt

from contexts.infrastructure.exceptions.not_found_error import NotFoundError
from contexts.domain.constants.database import DatabaseConstants
from contexts.infrastructure.database.sqlite_client import SQLiteClient


class AuthRepository:
    salt: bytes = bcrypt.gensalt()

    def __init__(self, sql_client: SQLiteClient):
        self.__sqlite_client = sql_client

    def create_table(self):
        self.__sqlite_client.execute_non_query(f'''
                    CREATE TABLE IF NOT EXISTS {DatabaseConstants.USER_TABLE} (
                        id TEXT PRIMARY KEY,
                        {DatabaseConstants.USERNAME_FIELD_NAME} TEXT,
                        {DatabaseConstants.PASSWORD_FIELD_NAME} TEXT
                    )
                ''')

    def init_default_user(self):
        password_hash = AuthRepository.get_hash("admin")
        self.__sqlite_client.execute_non_query(
            f'''insert into {DatabaseConstants.USER_TABLE} 
                    (id, {DatabaseConstants.USERNAME_FIELD_NAME}, {DatabaseConstants.PASSWORD_FIELD_NAME}) values(?, ?, ?)''',
            (uuid.uuid4().__str__(), "admin", password_hash))

    @staticmethod
    def get_hash(_string: str) -> bytes:
        return bcrypt.hashpw(_string.encode(), AuthRepository.salt)

    @staticmethod
    def validate(_password: bytes, _hash: bytes):
        return bcrypt.checkpw(_password, _hash)

    def insert(self, username: str, password: str):
        password_hash = AuthRepository.get_hash(password).decode()
        self.__sqlite_client.execute_non_query(
            f'''INSERT INTO {DatabaseConstants.USER_TABLE} 
            (id, {DatabaseConstants.USERNAME_FIELD_NAME}, {DatabaseConstants.PASSWORD_FIELD_NAME}) VALUES (?, ?, ?)''',
            (uuid.uuid4().__str__(), username, password_hash))

    def get_by_username(self, username: str) -> list:
        result = self.__sqlite_client.execute_query(
            f'select * from {DatabaseConstants.USER_TABLE} where {DatabaseConstants.USERNAME_FIELD_NAME} = ?',
            (username,))
        return list(result[0]) if len(result) > 0 else []

    def update_username(self, username_old: str, username_new: str):
        username = self.get_by_username(username_old)
        if len(username) == 0:
            raise NotFoundError
        self.__sqlite_client.execute_non_query(
            f"UPDATE {DatabaseConstants.USER_TABLE} SET {DatabaseConstants.USERNAME_FIELD_NAME}=? WHERE id=?",
            (username_new, username[0]))

    def update_username_by_id(self, _id: str, username_new: str):
        self.__sqlite_client.execute_non_query(
            f"UPDATE {DatabaseConstants.USER_TABLE} SET {DatabaseConstants.USERNAME_FIELD_NAME}=? WHERE id=?",
            (username_new, _id))

    def update_password(self, username: str, password: str):
        password_hash = AuthRepository.get_hash(password).decode()
        username = self.get_by_username(username)[0]
        if len(username) == 0:
            raise NotFoundError
        self.__sqlite_client.execute_non_query(
            f"UPDATE {DatabaseConstants.USER_TABLE} SET {DatabaseConstants.PASSWORD_FIELD_NAME}=? WHERE id=?",
            (password_hash, username[0]))

    def update_password_by_id(self, _id: str, password: str):
        password_hash = AuthRepository.get_hash(password).decode()
        self.__sqlite_client.execute_non_query(
            f"UPDATE {DatabaseConstants.USER_TABLE} SET {DatabaseConstants.PASSWORD_FIELD_NAME}=? WHERE id=?",
            (password_hash, _id))

    def update(self, username: str, username_new: str, password: str):
        user = self.get_by_username(username)
        if len(user) == 0:
            raise NotFoundError
        self.update_username_by_id(user[0], username_new)
        self.update_password_by_id(user[0], password)
