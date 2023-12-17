import system.global_vars


class ComicChapterDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, comic_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from comic_chapter where comic_id = \'' + str(comic_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, comic_id, chapter_name, seq_no):
        count = self.count(comic_id, chapter_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into comic_chapter(comic_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(comic_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(seq_no) + '\', 1, now(3), now(3))')
            self.conn.commit()

    def get_comic_chapter_id(self, comic_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute('select comic_chapter_id from comic_chapter where comic_id = \'' + str(comic_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result
