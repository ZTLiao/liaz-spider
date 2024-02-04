import system.global_vars


class NovelChapterItemDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, novel_chapter_id, novel_id, seq_no):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter_item where novel_chapter_id = \'' + str(novel_chapter_id) + '\' and novel_id = \'' + str(novel_id) + '\' and seq_no = \'' + str(seq_no) + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def save(self, novel_chapter_id, novel_id, path, seq_no):
        if path is None:
            print('novel_chapter_id : ', novel_chapter_id, ', novel_id : ', novel_id, ', seq_no : ', seq_no)
            return
        count = self.count(novel_chapter_id, novel_id, seq_no)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel_chapter_item(novel_chapter_id, novel_id, path, seq_no, created_at, updated_at) values(\'' + str(novel_chapter_id) + '\', \'' + str(novel_id) + '\', \'' + path + '\', \'' + str(seq_no) + '\', now(3), now(3))')
            self.conn.commit()
