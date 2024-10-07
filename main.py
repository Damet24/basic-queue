import logging

from queue import Queue
from server import Server

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    queue = Queue('queue.db')
    server = Server(queue=queue, logger=logger)
    server.start_server()
