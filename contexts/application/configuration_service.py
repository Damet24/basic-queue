from logging import Logger
from pathlib import Path

from contexts.application.base_service import BaseService
from contexts.infrastructure.database.auth_repository import AuthRepository
from contexts.infrastructure.database.data_repository import DataRepository


class ConfigurationService(BaseService):
    def __init__(self, auth_repository: AuthRepository, data_repository: DataRepository):
        super().__init__()
        self.__file = Path('data.json')
        self.__auth_repository = auth_repository
        self.__data_repository = data_repository
        self.__check_configuration()

    def __check_configuration(self):
        if not self.__file.exists():
            self.logger.info("configuration is being initialized")
            self.__initialize()
            self.logger.info("the configuration has finished initializing")

    def __initialize(self):
        self.__file.touch()
        self.__auth_repository.create_table()
        self.__auth_repository.init_default_user()
        self.__data_repository.create_table()
