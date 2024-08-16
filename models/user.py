class User:
    def __init__(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name

    def get_id(self):
        return self.user_id

    def get_email(self):
        return self.email

    def get_name(self):
        return self.name
