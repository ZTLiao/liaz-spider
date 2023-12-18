import system.global_vars


class ComicChapterItemDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, comic_chapter_id, comic_id, seq_no):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from comic_chapter_item where comic_chapter_id = \'' + str(comic_chapter_id) + '\' and comic_id = \'' + str(comic_id) + '\' and seq_no = \'' + str(seq_no) + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, comic_chapter_id, comic_id, path, seq_no):
        if path is None:
            print('comic_chapter_id : ', comic_chapter_id, ', comic_id : ', comic_id, ', seq_no : ', seq_no)
            return
        count = self.count(comic_chapter_id, comic_id, seq_no)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into comic_chapter_item(comic_chapter_id, comic_id, path, seq_no, created_at, updated_at) values(\'' + str(comic_chapter_id) + '\', \'' + str(comic_id) + '\', \'' + path + '\', \'' + str(seq_no) + '\', now(3), now(3))')
            self.conn.commit()
