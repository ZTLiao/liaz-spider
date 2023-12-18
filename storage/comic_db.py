import system.global_vars


class ComicDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, title):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from comic where title = \'' + title + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, title, cover, description, category_ids, categories, author_ids,
             authors, region):
        count = self.count(title)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into comic(title, cover, description, first_letter, direction, flag, category_ids, categories, author_ids, authors, region_id, region, chapter_num, start_time, end_time, subscribe_num, hit_num, status, created_at, updated_at) values(\'' + title + '\', \'' + cover + '\', \'' + description + '\', \'\', 0, 0, \'' + category_ids + '\', \'' + categories + '\', \'' + author_ids + '\', \'' + authors + '\', 0, \'' + region + '\', 0, now(3), now(3), 0, 0, 1, now(3), now(3))')
            self.conn.commit()

    def get_comic_id(self, title):
        cursor = self.conn.cursor()
        cursor.execute('select comic_id from comic where title = \'' + title + '\' limit 1')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result
