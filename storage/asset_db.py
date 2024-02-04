import system.global_vars
import pymysql


class AssetDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, obj_id, asset_type):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select count(1) from asset where obj_id = \'' + str(obj_id) + '\' and asset_type = \'' + str(
            asset_type) + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, asset_key, asset_type, title, cover, obj_id, category_ids, author_ids):
        count = self.count(obj_id, asset_type)
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        if count == 0:
            cursor = conn.cursor()
            cursor.execute(
                'insert into asset(asset_key, asset_type, title, cover, obj_id, category_ids, author_ids, created_at, updated_at) values(\'' + asset_key + '\', \'' + str(
                    asset_type) + '\', \'' + title + '\', \'' + cover + '\', \'' + str(
                    obj_id) + '\', \'' + category_ids + '\', \'' + author_ids + '\', now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def update(self, obj_id, asset_type, upgrade_chapter, chapter_id):
        if chapter_id is None:
            return
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'update asset set upgrade_chapter = \'' + upgrade_chapter + '\', chapter_id = \'' + str(
                chapter_id) + '\', updated_at = now(3) where obj_id = \'' + str(
                obj_id) + '\' and asset_type = \'' + str(asset_type) + '\'')
        cursor.close()
        conn.close()
