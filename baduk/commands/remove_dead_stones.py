from baduk.commands.command_types import UndoableCommand


class RemoveDeadStones(UndoableCommand):

    def __init__(self, groups, dead_stones):
        self.groups = groups
        self.group = None
        self.dead_stones = dead_stones

    def execute(self):
        if len(self.dead_stones) > 0:
            for dead_stones in self.dead_stones:
                dead_stones.remove_stones()
                self.groups.remove(dead_stones)

    def undo(self):
        for dead_stone in self.dead_stones:
            self.groups.add(dead_stone)
