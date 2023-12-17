class Application:
    def __init__(self):
        self.__env = None
        self.__name = None

    def set_env(self, env: str):
        self.__env = env

    def get_env(self):
        return self.__env

    def set_name(self, name: str):
        self.__name = name

    def get_name(self):
        return self.__name
