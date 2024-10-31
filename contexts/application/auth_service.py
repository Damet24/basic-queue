from contexts.application.base_service import BaseService
from contexts.infrastructure.exceptions.not_found_error import NotFoundError
from contexts.infrastructure.database.auth_repository import AuthRepository


class AuthService(BaseService):
    def __init__(self, auth_repository: AuthRepository):
        super().__init__()
        self.__auth_repository = auth_repository

    def _validate_password(self, password: bytes, _hash: bytes) -> bool:
        return AuthRepository.validate(password, _hash)

    def create(self, username: str, password: str):
        info = self.__auth_repository.get_by_username(username)
        if info:
            return "Error\r\nusername already exists"
        self.__auth_repository.insert(username, password)
        return "Ok"

    def validate(self, credentials: list[str]) -> bool:
        info = self.__auth_repository.get_by_username(credentials[0])
        if len(info) > 0:
            self.logger.debug(info.__str__())
            return self._validate_password(info[1].encode(), info[2] if type(info[2]) is bytes else info[2].encode())
        return False

    def get_by_username(self, username: str):
        return self.__auth_repository.get_by_username(username)

    def update_username(self, username: str, new_username: str):
        try:
            self.logger.debug('updating username...')
            self.__auth_repository.update_username(username, new_username)
            return "Ok"
        except NotFoundError:
            return "Ok\r\nusername not exists"

    def update_password(self, username: str, password: str):
        try:
            self.__auth_repository.update_password(username, password)
            return "Ok"
        except NotFoundError:
            return "Error\r\nusername not exists"

    def update(self, username: str, new_username: str, password: str):
        try:
            self.__auth_repository.update(username, new_username, password)
            return "Ok"
        except NotFoundError:
            return "Error\r\nusername not exists"
