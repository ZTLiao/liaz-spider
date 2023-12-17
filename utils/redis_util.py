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
            print('hget ', name, ' is error.', e)
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


# if __name__ == '__main__':
#     util = RedisUtil(host='172.22.0.8', port=6379, db=0, password='pc8DphhaXwTe2jyv')
#     room = util.hgetall('peko_room_mic_up')
#     if len(room) == 0:
#         print('room is empty')
#     else:
#         print(room)
#         for keyByte, valueByte in room.items():
#             key = keyByte.decode('utf-8')
#             value = valueByte.decode('utf-8')
#             print(key)
#             util.hdel('peko_uid_ticket', key)
#             data = json.loads(value)
#             micUsers = data['micUsers']
#             for user in micUsers:
#                 print(user['uid'])
#                 util.hdel('peko_uid_ticket', user['uid'])