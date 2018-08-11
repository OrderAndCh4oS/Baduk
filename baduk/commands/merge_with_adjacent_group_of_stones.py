from baduk.commands.command_types import UndoableCommand
from baduk.enums import Stone
from baduk.stones.group_of_stones import GroupOfStones


class MergeWithAdjacentGroupsOfStones(UndoableCommand):

    def __init__(self, groups, stone_link, adjacent_stones):
        self.stone_link = stone_link
        self.adjacent_stones = adjacent_stones
        self.groups = groups
        self.group = None
        self.old_groups = set()

    # Todo: Command + Undo: remove the new group, add the old groups, update the links group
    def execute(self, **kwargs):
        self.group = GroupOfStones(self.stone_link)
        for adjacent_stone in self.adjacent_stones:
            self.old_groups.add(adjacent_stone.group)
            self.group.merge(adjacent_stone.group)
        for old_group in self.old_groups:
            self.groups.remove(old_group)
        self.group.set_links_group()
        self.groups.add(self.group)
        return self.group

    def undo(self):
        self.stone_link.stone = Stone.NONE
        self.groups.remove(self.group)
        for old_group in self.old_groups:
            self.groups.add(old_group)
