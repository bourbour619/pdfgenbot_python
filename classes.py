import os
from os import path

class Activity :
    id = ''
    root = ''
    accepted = ['pdf', 'doc', 'docx', 'jpeg', 'jpg', 'png']
    current = ''
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
    
    def remove(self, name) -> None:
        current = path.join(self.root, name)
        if path.isfile(current):
            os.remove(current)

    def flush(self) -> None:
        os.system(f'rm -rf {self.root}')
        self.id = ''
        self.root = ''



