import uuid
from collections import deque

from database import Database


class Queue:
    def __init__(self, database: str):
        self.queue = deque()
        self.db = Database(database)

    def enqueue(self, content: str):
        _id = uuid.uuid4()
        self.queue.append({'id': _id.__str__(), 'content': content})
        self.db.insert(_id.__str__(), content)

    def enqueue_batch(self, iterable):
        self.queue.extend([{'id': _item[0], 'content': _item[1]} for _item in iterable])
        self.db.insert_many(iterable)

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
