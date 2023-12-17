class Comic:
    def __init__(self, comic_id, title, cover, description, first_letter, flag, category_ids, categories, author_ids, authors, chapter_num, start_time, end_time, subscribe_num, hit_num, status, created_at, updated_at):
        self.comic_id = comic_id
        self.title = title
        self.cover = cover
        self.description = description
        self.first_letter = first_letter
        self.flag = flag
        self.category_ids = category_ids
        self.categories = categories
        self.author_ids = author_ids
        self.authors = authors
        self.chapter_num = chapter_num
        self.start_time = start_time
        self.end_time = end_time
        self.subscribe_num = subscribe_num
        self.hit_num = hit_num
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
