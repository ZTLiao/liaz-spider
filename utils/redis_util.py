import json

import redis


class RedisUtil:
    def __init__(self, host, port, db, password):
        self.host = host
        self.port = port
        self.db = db
        self.password = password

    def scan(self, match: str):
        keys = []
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            cursor = 0
            while True:
                tup = res.scan(cursor=cursor, match=match, count=1000)
                print(tup)
                if isinstance(tup[0], int):
                    cursor = tup[0]
                if isinstance(tup[1], list):
                    keys.extend(tup[1])
                if cursor == 0:
                    break
        except Exception as e:
            print('scan is error.', e)
        finally:
            res.close()
        return keys

    def delete(self, name: str):
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            res.delete(name)
        except Exception as e:
            print('delete ', name, ' is error.', e)
        finally:
            res.close()

    def hgetall(self, name: str):
        data = None
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            data = res.hgetall(name)
        except Exception as e:
            print('hgetall ', name, ' is error.', e)
        finally:
            res.close()
        return data

    def hincrby(self, name: str, field, increment):
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            res.hincrby(name, field, increment)
        except Exception as e:
            print('hincrby ', name, ' is error.', e)
        finally:
            res.close()

    def hdel(self, name: str, field):
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            res.hdel(name, field)
        except Exception as e:
            print('hdel ', name, ' is error.', e)
        finally:
            res.close()

    def hget(self, name: str, field):
        data = None
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            data = res.hget(name, field)
        except Exception as e:
            print('hget ', name, ' is error.', e)
        finally:
            res.close()
        return data

    def zrange(self, name: str, start: int, end: int, withscores: bool):
        data = None
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            data = res.zrange(name, start=start, end=end, withscores=withscores)
        except Exception as e:
            print('zrange ', name, ' is error.', e)
        finally:
            res.close()
        return data

    def zincrby(self, name: str, amount: float, value: str):
        res = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
        try:
            res.zincrby(name, amount, value)
        except Exception as e:
            print('zincrby ', name, ' is error.', e)
        finally:
            res.close()


