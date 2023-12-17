from config.mysql_config import MySqlConfig
from config.nacos_config import NacosConfig
from config.redis_config import RedisConfig
import re


class SystemConfig:
    def __init__(self):
        self.__nacos = NacosConfig()
        yaml_conf = self.__nacos.yaml_conf
        for config in yaml_conf:
            if 'redis' in config:
                redis = config['redis']
                self.__redis = RedisConfig(redis['host'], redis['port'], redis['db'], redis['password'])
            if 'database' in config:
                database = config['database']
                url = database['url']
                result = re.match(
                    r"tcp\((?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(?P<port>\d+)\)\/(?P<database>\w+)", url)
                if result:
                    host = result.group('ip_address')
                    port = result.group('port')
                    db = result.group('database')
                    self.__mysql = MySqlConfig(host, port, database['username'], database['password'], db)
                else:
                    print("No match found.")

    def get_nacos(self):
        return self.__nacos

    def get_redis(self):
        return self.__redis

    def get_mysql(self):
        return self.__mysql
