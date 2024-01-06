import system.global_vars


class AssetDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, obj_id, asset_type):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from asset where obj_id = \'' + str(obj_id) + '\' and asset_type = \'' + str(
            asset_type) + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, asset_key, asset_type, title, cover, obj_id, category_ids, author_ids):
        count = self.count(obj_id, asset_type)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into asset(asset_key, asset_type, title, cover, obj_id, category_ids, author_ids, created_at, updated_at) values(\'' + asset_key + '\', \'' + str(
                    asset_type) + '\', \'' + title + '\', \'' + cover + '\', \'' + str(obj_id) + '\', \'' + category_ids + '\', \'' + author_ids + '\', now(3), now(3))')
            self.conn.commit()

    def update(self, obj_id, asset_type, upgrade_chapter, chapter_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'update asset set upgrade_chapter = \'' + upgrade_chapter + '\', chapter_id = \'' + str(chapter_id) + '\', updated_at = now(3) where obj_id = \'' + str(obj_id) + '\' and asset_type = \'' + str(asset_type) + '\'')
