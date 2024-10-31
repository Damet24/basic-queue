import sys

from apps.server.container import ServerContainer
from apps.cli import main, __app_name__

# def main(app_type: str) -> None:
#     if app_type == 'server':
#         container = ServerContainer()
#         container.config.from_ini('./server/config.ini')
#         container.init_resources()
#         container.wire(modules=[__name__])
#         server = container.server()
#         server.start_server()
#     else:
#         print('cli app')


if __name__ == '__main__':
    # main(*sys.argv[1:])
    main.app()
