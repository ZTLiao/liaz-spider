import time
from constants import constant


class Response:
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = time.time()


def ok(data=None):
    return Response(200, constant.SUCCESS, data)


def fail():
    return Response(500, constant.FAIL, None)
