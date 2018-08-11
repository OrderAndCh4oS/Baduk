from baduk.commands.add_to_adjacent_group_of_stones import AddToAdjacentGroupOfStones
from baduk.commands.chain_of_command import ChainOfCommands
from baduk.commands.create_group_of_stones import CreateNewGroupOfStones
from baduk.commands.merge_with_adjacent_group_of_stones import MergeWithAdjacentGroupsOfStones
from baduk.commands.remove_dead_stones import RemoveDeadStones
from baduk.stones.stone_link import StoneLink


class GroupOfStonesCollection:

    def __init__(self):
        self.groups = set()
        self.dead_stone_count = 0
        self.chain_of_commands = ChainOfCommands()

    def add_stone_link(self, stone_link: StoneLink, board):
        group = self.add_stone_link_to_group_of_stones(board, stone_link)
        self.update_groups_of_stones(board)
        dead_stones = self.find_dead_stones(group)
        self.dead_stone_count = self.count_dead_stones(dead_stones)
        if not self.has_dead_stones() and group.get_liberties() == 0:
            self.chain_of_commands.undo()
            return False
        else:
            self.remove_dead_stones(dead_stones)
            return True

    def update_groups_of_stones(self, board):
        for group in self.groups:
            group.update(board)

    # Todo: Chain of Responsibility
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
            if group.get_liberties() == 0 and str(group) != str(current_group):
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
