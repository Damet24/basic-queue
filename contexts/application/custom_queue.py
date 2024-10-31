import uuid
from collections import deque

from contexts.application.base_service import BaseService
from contexts.infrastructure.database.data_repository import DataRepository


class Queue(BaseService):
    def __init__(self, data_repository: DataRepository):
        super().__init__()
        self.queue = deque()
        self.db = data_repository

    def enqueue(self, content: str):
        _id = uuid.uuid4()
        self.queue.append({'id': _id.__str__(), 'content': content})
        self.db.insert(_id.__str__(), content)

    def enqueue_batch(self, iterable):
        data = [{'id': uuid.uuid4().__str__(), 'content': _item} for _item in iterable]
        self.queue.extend(data)
        self.db.insert_many(data)

    def dequeue(self):
        if self.queue:
            item = self.queue.popleft()
            self.db.mark_processed(item['id'])
            return item
        return None

    def dequeue_batch(self, quantity=1):
        items = []
        if self.queue:
            for i in range(quantity):
                items.append(self.dequeue())
        return items

    def get_all(self):
        return list(self.queue)

    def get_processed(self):
        return self.db.fetch_all()
