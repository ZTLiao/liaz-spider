import system.global_vars


class NovelChapterDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, novel_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter where novel_id = \'' + str(novel_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, novel_id, chapter_name, seq_no):
        count = self.count(novel_id, chapter_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel_chapter(novel_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(novel_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(seq_no) + '\', 1, now(3), now(3))')
            self.conn.commit()

    def get_novel_chapter_id(self, novel_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute('select novel_chapter_id from novel_chapter where novel_id = \'' + str(novel_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result
