import os
from os import path

class Activity :
    id = ''
    root = ''
    def __init__(self) -> None:
        pass

    def init(self, id):
        self.id = id
        self.root = path.join(path.join(path.dirname(__file__),'files'), self.id)
        if self.first() :
            self.env()

    def first(self) -> bool:
        return not path.isdir(self.root)

    def env(self) -> None:
        os.mkdir(self.root)

    def log(self) -> list:
        return os.listdir(self.root)

    def add(self, name) -> str:
        return path.join(self.root, name)