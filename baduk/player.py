from baduk.enums import Stone


class Player:
    def __init__(self, name, stone: Stone):
        self.stone = stone
        self.name = name

    def get_stone(self):
        return self.stone

    def __str__(self):
        return self.name