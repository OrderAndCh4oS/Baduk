from baduk.command.command_types import UndoableCommand
from baduk.stones.group_of_stones import GroupOfStones
from baduk.stones.stone_link import StoneLink


class MergeWithAdjacentGroupsOfStones(UndoableCommand):

    def __init__(self, groups: set, stone_link: StoneLink, adjacent_stones: list):
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
        self.group.remove_stone_from_board(self.stone_link)
        self.groups.remove(self.group)
        for old_group in self.old_groups:
            old_group.set_links_group()
            self.groups.add(old_group)
