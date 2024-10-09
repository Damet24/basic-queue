import json
import re

from queue import Queue


class RequestProcessor:

    @classmethod
    def encode(cls, data) -> str:
        return json.dumps(data)

    @classmethod
    def parse_headers(cls, input_string: str) -> dict:
        pattern = r'\[(\w+)=([^\[\]]+)\]'
        matches = re.findall(pattern, input_string)

        result = {}
        for key, value in matches:
            if ':' in value:
                result[key] = value.split(':')
            else:
                result[key] = value
        return result

    @classmethod
    def parse_body(cls, input_string: str):
        return input_string.split(':', 1)

    @classmethod
    def decode(cls, data: str) -> dict[str, str]:
        [headers, body] = data.split("\r\n", 1)
        body_parsed = cls.parse_body(body)
        headers_parsed = cls.parse_headers(headers)
        return {
            "command": body_parsed[0],
            "content": body_parsed[1],
            "headers": headers_parsed
        }

    @classmethod
    def process_command(cls, q: Queue, command_type: str, param: str):
        process_method = getattr(cls, f"_process_{command_type}_command", cls._process_not_exists_command)
        return process_method(cls, q, param)

    def _process_not_exists_command(self, q: Queue, param: str):
        return "Command not exists"

    def _process_add_command(self, q: Queue, param: str):
        q.enqueue(param)
        return "Ok"

    def _process_get_command(self, q: Queue, param: str):
        return json.dumps(q.dequeue())

    def _process_fetch_command(self, q: Queue, param: str):
        return json.dumps(q.get_all())