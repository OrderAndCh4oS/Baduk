from baduk.command.add_to_adjacent_group_of_stones import AddToAdjacentGroupOfStones
from baduk.command.chain_of_command import ChainOfCommands
from baduk.command.create_group_of_stones import CreateNewGroupOfStones
from baduk.command.merge_with_adjacent_group_of_stones import MergeWithAdjacentGroupsOfStones
from baduk.command.remove_dead_stones import RemoveDeadStones
from baduk.stones.stone_link import StoneLink
from baduk.validation.move_validation import MoveValidation


class GroupOfStonesCollection:

    def __init__(self):
        self.groups = set()
        self.dead_stone_count = 0
        self.chain_of_commands = ChainOfCommands()

    def add_stone_link(self, stone_link: StoneLink, board):
        group = self.add_stone_link_to_group_of_stones(board, stone_link)
        self.update_adjacent_groups_of_stones(board, group, stone_link)
        dead_stones = self.find_dead_stones(group)
        self.dead_stone_count = self.count_dead_stones(dead_stones)
        MoveValidation.check_self_capture(group, self.has_dead_stones(), self.chain_of_commands)
        self.remove_dead_stones(dead_stones)
        MoveValidation.breaks_simple_ko_rule(self, dead_stones, board)

    def update_adjacent_groups_of_stones(self, board, group, stone_link):
        adjacent_groups = {link.group for link in stone_link.get_adjacent_groups(board)}
        adjacent_groups.add(group)
        self.update_groups_of_stones(board, adjacent_groups)

    def update_groups_of_stones(self, board, groups=None):
        for group in groups if groups else self.groups:
            group.update(board)

    def add_stone_link_to_group_of_stones(self, board, stone_link):
        adjacent_stones = list(stone_link.get_adjacent_stones(board))
        if len(adjacent_stones) > 1:
            group = self.chain_of_commands.execute_command(
                MergeWithAdjacentGroupsOfStones(self.groups, stone_link, adjacent_stones)
            )
        elif len(adjacent_stones) == 1:
            group = self.chain_of_commands.execute_command(
                AddToAdjacentGroupOfStones(self.groups, stone_link, adjacent_stones)
            )
        else:
            group = self.chain_of_commands.execute_command(
                CreateNewGroupOfStones(self.groups, stone_link)
            )
        return group

    def find_dead_stones(self, current_group):
        dead_stones = set()
        for group in self.groups:
            # Todo: for class instance comparison classes should implement __hash__ and/or __eq__
            if group.get_liberties() == 0 and group != current_group:
                dead_stones.add(group)
        return dead_stones

    def has_dead_stones(self):
        return self.dead_stone_count > 0

    def count_dead_stones(self, dead_stones):
        count = 0
        for dead_stones in dead_stones:
            count += len(dead_stones.get_links()) if dead_stones else 0
        return count

    def get_dead_stones_count(self):
        return self.dead_stone_count

    def remove_dead_stones(self, dead_stones):
        self.chain_of_commands.execute_command(
            RemoveDeadStones(self.groups, dead_stones)
        )

    def rollback(self):
        self.chain_of_commands.undo()
        self.chain_of_commands.undo()

    def reset(self):
        self.groups = set()
        self.dead_stone_count = 0
        self.chain_of_commands.reset()
