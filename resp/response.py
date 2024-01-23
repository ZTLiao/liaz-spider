import time
from constants import status


class Response:
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = time.time()


def ok(data=None):
    return Response(200, status.SUCCESS, data)


def fail():
    return Response(500, status.FAIL, None)
