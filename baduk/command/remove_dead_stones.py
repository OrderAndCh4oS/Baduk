from baduk.command.command_types import UndoableCommand


class RemoveDeadStones(UndoableCommand):

    def __init__(self, groups: set, dead_stone_groups: list):
        self.groups = groups
        self.group = None
        self.dead_stone_groups = dead_stone_groups

    def execute(self):
        if len(self.dead_stone_groups) > 0:
            for dead_stone_group in self.dead_stone_groups:
                dead_stone_group.capture_stones()
                self.groups.remove(dead_stone_group)

    def undo(self):
        for dead_stone_group in self.dead_stone_groups:
            dead_stone_group.replace_captured_stones()
            self.groups.add(dead_stone_group)
