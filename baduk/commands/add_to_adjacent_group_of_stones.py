from baduk.commands.command_types import UndoableCommand
from baduk.enums import Stone


class AddToAdjacentGroupOfStones(UndoableCommand):

    def __init__(self, groups, stone_link, adjacent_stones):
        self.stone_link = stone_link
        self.adjacent_stones = adjacent_stones
        self.groups = groups
        self.group = None

    # Todo: Command + Undo: remove stone_link from group
    def execute(self, **kwargs):
        adjacent_stone = self.adjacent_stones[0]
        self.group = adjacent_stone.group
        self.group.add_link(self.stone_link)
        return self.group

    def undo(self):
        self.stone_link.stone = Stone.NONE
        self.groups.remove(self.group)
