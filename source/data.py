usersDict = {}


class User:
    def __init__(self, name=None, age=None, description=None, photo=None, id=None, username=None, chat_id=None):
        self.name = name
        self.age = age
        self.description = description
        self.photo = photo

        self.id = id
        self.username = username
        self.chat_id = chat_id

        self.liked = set()
        self.was_liked = []
        self.viewed = set()
        self.last_viewed = None

        self.requested = list()
        self.friends = list()

        self.status = None

    def About(self):
        return f'{self.name}, {self.age}\n\n{self.description}'
