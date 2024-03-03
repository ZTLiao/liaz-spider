class Application:
    def __init__(self):
        self.__env = None
        self.__name = None
        self.__mysql = None
        self.__close_status: int = 0

    def set_env(self, env: str):
        self.__env = env

    def get_env(self):
        return self.__env

    def set_name(self, name: str):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_mysql(self, mysql):
        self.__mysql = mysql

    def get_mysql(self):
        return self.__mysql

    def set_close_status(self, close_status: int):
        self.__close_status = close_status

    def get_close_status(self):
        return self.__close_status
