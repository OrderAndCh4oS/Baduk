from baduk.commands.command_types import UndoableCommand
from baduk.stones.group_of_stones import GroupOfStones


class CreateNewGroupOfStones(UndoableCommand):

    def __init__(self, groups, stone_link):
        self.stone_link = stone_link
        self.groups = groups
        self.group = None

    # Todo: Command + Undo: remove the new group
    def execute(self, **kwargs):
        self.group = GroupOfStones(self.stone_link)
        self.groups.add(self.group)
        return self.group

    def undo(self):
        self.groups.remove(self.group)
