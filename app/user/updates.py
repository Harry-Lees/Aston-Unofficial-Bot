class Update:
    def __init__(self, _type, title, text):
        self.type = _type
        self.title = title
        self.text = text

    def __str__(self):
        return f'{self.type} {self.title} {self.text}'