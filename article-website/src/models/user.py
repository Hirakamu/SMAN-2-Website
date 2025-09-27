class User:
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    def __repr__(self):
        return f"<User {self.username}>"