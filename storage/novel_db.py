import system.global_vars


class NovelDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, title):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from novel where title = \'' + title + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def save(self, title, cover, description, flag, category_ids, categories, author_ids,
             authors, region_id, region):
        count = self.count(title)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel(title, cover, description, first_letter, direction, flag, category_ids, categories, author_ids, authors, region_id, region, chapter_num, start_time, end_time, subscribe_num, hit_num, status, created_at, updated_at) values(\'' + title + '\', \'' + cover + '\', \'' + description + '\', \'\', 0, \'' + str(
                    flag) + '\', \'' + category_ids + '\', \'' + categories + '\', \'' + author_ids + '\', \'' + authors + '\', \'' + str(
                    region_id) + '\', \'' + region + '\', 0, now(3), now(3), 0, 0, 1, now(3), now(3))')
            self.conn.commit()

    def get_novel_id(self, title):
        cursor = self.conn.cursor()
        cursor.execute('select novel_id from novel where title = \'' + title + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def upgrade(self, novel_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'update novel set end_time = now(3) where novel_id = \'' + str(novel_id) + '\'')
