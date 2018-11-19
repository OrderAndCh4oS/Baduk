from baduk.enums.enums import Stone


class Player:
    def __init__(self, name, stone: Stone):
        self.stone = stone
        self.name = name
        self.killed_stones = 0

    def get_stone(self):
        return self.stone

    def update_killed_stone_count(self, killed_stone_count):
        self.killed_stones += killed_stone_count

    def __str__(self):
        return self.name
