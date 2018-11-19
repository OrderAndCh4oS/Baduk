from baduk.command.command_types import UndoableCommand
from baduk.stones.group_of_stones import GroupOfStones
from baduk.stones.stone_link import StoneLink


class CreateNewGroupOfStones(UndoableCommand):

    def __init__(self, groups: set, stone_link: StoneLink):
        self.stone_link = stone_link
        self.groups = groups
        self.group = None

    # Todo: Command + Undo: remove the new group
    def execute(self, **kwargs):
        self.group = GroupOfStones(self.stone_link)
        self.groups.add(self.group)
        return self.group

    def undo(self):
        self.group.remove_stone_from_board(self.stone_link)
        self.groups.remove(self.group)
