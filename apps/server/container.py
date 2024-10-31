import logging.config
from dependency_injector import containers, providers

from apps.server.request import RequestProcessor
from apps.server.server import Server
from contexts.application.auth_service import AuthService
from contexts.application.configuration_service import ConfigurationService
from contexts.application.custom_queue import Queue
from contexts.infrastructure.database.auth_repository import AuthRepository
from contexts.infrastructure.database.data_repository import DataRepository
from contexts.infrastructure.database.sqlite_client import SQLiteClient


class ServerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.fileConfig,
        fname="logging.ini",
    )

    sql_client = providers.Singleton(SQLiteClient, config.database.name)

    auth_repository = providers.Singleton(AuthRepository, sql_client)
    data_repository = providers.Singleton(DataRepository, sql_client)

    config_service = providers.Singleton(ConfigurationService, auth_repository, data_repository)
    queue_service = providers.Singleton(Queue, data_repository)
    auth_service = providers.Singleton(AuthService, auth_repository)

    request_processor = providers.Singleton(RequestProcessor, auth_service)

    server = providers.Singleton(Server, config_service, queue_service, auth_service, request_processor)
