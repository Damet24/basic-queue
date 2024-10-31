import json
import re
from dataclasses import dataclass

from inject import params

from contexts.infrastructure.exceptions.break_loop_exception import BreakLoopException
from contexts.infrastructure.exceptions.not_found_error import NotFoundError
from contexts.domain.constants.database import DatabaseConstants
from contexts.application.custom_queue import Queue
from contexts.application.auth_service import AuthService


@dataclass
class RequestProcessor:
    __auth_service: AuthService

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

    def process_command(self, queue: Queue, command_type: str, param: str):
        process_method = getattr(self, f"_process_{command_type}_command", self._process_not_exists_command)
        return process_method(queue, param)

    def process_queue_command(self, queue: Queue, command_type: str, param: str):
        raise BreakLoopException()

    def _process_not_exists_command(self, q: Queue, param: str):
        return "Command not exists"

    def _process_add_command(self, q: Queue, param: str):
        q.enqueue(param)
        return "Ok"

    def _process_add_batch_command(self, q: Queue, param: str):
        q.enqueue_batch(param)
        return "Ok"

    def _process_get_command(self, q: Queue, param: str):
        return f"Ok\r\n{json.dumps(q.dequeue())}"

    def _process_get_batch_command(self, q: Queue, param: str):
        return f"Ok\r\n{json.dumps(q.dequeue_batch(int(param)))}"

    def _process_fetch_command(self, q: Queue, param: str):
        return f"Ok\n\r{json.dumps(q.get_all())}"

    def _process_config_command(self, q: Queue, params: str):
        primary, secondary, *params = json.loads(params)['params']
        method = getattr(self, f"_process_config_command_{primary}_{secondary}", self._process_not_exists_command)
        return method(params)

    def _process_config_command_credentials_add(self, params) -> str:
        if len(params) < 2:
            return "Error\r\n2 arguments minimum expected"
        if len(params[1]) < 8:
            return "Error\r\nThe password must contain 8 or more characters"
        if params[0] == DatabaseConstants.USERNAME_FIELD_NAME:
            return "Error\r\ninvalid username"
        return self.__auth_service.create(params[0], params[1])

    def _process_config_command_credentials_edit(self, params) -> str:
        try:
            if len(params) < 3:
                return "Error\r\n2 arguments minimum expected"

            if params[0] == DatabaseConstants.USERNAME_FIELD_NAME:
                return self.__auth_service.update_username(params[1], params[2])

            elif params[0] == DatabaseConstants.PASSWORD_FIELD_NAME:
                if len(params[2]) < 8:
                    return "Error\r\nThe password must contain 8 or more characters"
                else:
                    return self.__auth_service.update_password(params[1], params[2])
            else:
                return self.__auth_service.update(params[0], params[1], params[2])
        except NotFoundError:
            return "Error\r\nusername not exists"
