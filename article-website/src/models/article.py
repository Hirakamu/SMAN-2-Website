class Article:
    def __init__(self, id, title, content, user_id, is_trashed=False):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.is_trashed = is_trashed

    def __repr__(self):
        return f"<Article {self.title}>"