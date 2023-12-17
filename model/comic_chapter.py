class ComicChapter:
    def __init__(self, comic_chapter_id, comic_id, chapter_name, chapter_type, page_num, seq_no, created_at, updated_at):
        self.comic_chapter_id = comic_chapter_id
        self.comic_id = comic_id
        self.chapter_name = chapter_name
        self.chapter_type = chapter_type
        self.page_num = page_num
        self.seq_no = seq_no
        self.created_at = created_at
        self.updated_at = updated_at
