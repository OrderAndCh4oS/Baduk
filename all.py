import os.path
import re
from abc import ABCMeta, abstractmethod
from enum import unique, Enum
from random import random, randint

ALPHA_KEY = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
    'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

HANDICAP_19_X_19 = ('16Q', '4D', '4Q', '16D', '10K', '10D', '10Q', '16K', '4K')
HANDICAP_13_X_13 = ('10K', '4D', '4K', '10D', '7G', '7D', '7K', '10G', '4G')
HANDICAP_9_X_9 = ('7G', '3C', '3G', '7C', '5E', '5C', '5G', '7E', '3E')


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


@unique
class Stone(Enum):
    WHITE = 'o'
    BLACK = 'x'
    NONE = '.'

    def __str__(self):
        return self.value


class Command(metaclass=ABCMeta):

    @abstractmethod
    def execute(self):
        pass


class UndoableCommand(Command, metaclass=ABCMeta):

    @abstractmethod
    def undo(self):
        pass


class ChainOfCommands:
    stack = []

    def execute_command(self, command: Command):
        result = command.execute()
        if isinstance(command, UndoableCommand):
            self.stack.append(command)
        return result

    def undo(self):
        if len(self.stack):
            command = self.stack.pop()
            command.undo()

    def reset(self):
        for command in self.stack:
            del command
        self.stack = []


class AddToAdjacentGroupOfStones(UndoableCommand):

    def __init__(self, groups: set, stone_link, adjacent_stones: list):
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
        self.group.remove_stone_from_board(self.stone_link)


class MergeWithAdjacentGroupsOfStones(UndoableCommand):

    def __init__(self, groups: set, stone_link, adjacent_stones: list):
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


class CreateNewGroupOfStones(UndoableCommand):

    def __init__(self, groups: set, stone_link):
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


class Point:
    coordinate = None
    x = None
    y = None

    def __init__(self, x=None, y=None, coordinate=None):
        if coordinate is not None and len(coordinate) > 3:
            raise ValidationError('Coordinate format is invalid')
        if coordinate:
            self.parse_coordinate(coordinate)
        elif x is not None and y is not None:
            self.parse_x_y(x, y)
        else:
            raise ValidationError('Needs to be passed a coordinate or x and y')

    def parse_coordinate(self, coordinate):
        self.coordinate = coordinate
        alpha = coordinate[-1:]
        self.x = int(ALPHA_KEY.index(alpha))
        self.y = int(coordinate[:-1]) - 1

    def parse_x_y(self, x, y):
        self.coordinate = '%d%s' % (y + 1, ALPHA_KEY[x])
        self.x = x
        self.y = y

    def adjacent_points(self):
        return [
            {"x": self.x + 1, "y": self.y},
            {"x": self.x - 1, "y": self.y},
            {"x": self.x, "y": self.y + 1},
            {"x": self.x, "y": self.y - 1}
        ]

    def map_adjacent_links(self, callback, board):
        for adjacent_point in self.adjacent_points():
            if board.in_grid(adjacent_point):
                yield callback(board.get_point_stone_link(**adjacent_point), board)

    def filter_adjacent_links(self, callback, board):
        for adjacent_point in self.adjacent_points():
            if board.in_grid(adjacent_point):
                link = board.get_point_stone_link(**adjacent_point)
                if callback(link):
                    yield link


class StoneLink:
    group = None

    def __init__(self, point, stone):
        self.point = point
        self.stone = stone

    def set_group(self, group):
        self.group = group

    def set_stone(self, stone):
        self.stone = stone

    def get_adjacent_stones(self, board):
        return self.point.filter_adjacent_links(
            lambda adjacent_link: self.stone == adjacent_link.stone,
            board
        )

    def find_adjacent(self, links, liberties, board):
        for adjacent_point in self.point.adjacent_points():
            if board.in_grid(adjacent_point):
                adjacent_link = board.get_point_stone_link(**adjacent_point)
                self.set_links_and_liberties(adjacent_link, board, liberties, links)

    def set_links_and_liberties(self, adjacent_link, board, liberties, links):
        if adjacent_link.stone == self.stone and adjacent_link not in links:
            links.add(adjacent_link)
            adjacent_link.find_adjacent(links, liberties, board)
        elif adjacent_link.stone == Stone.NONE:
            liberties.add(adjacent_link)


class GroupOfStones:
    def __init__(self, link: StoneLink):
        self.stone = link.stone
        self.links = set()
        self.liberties = set()
        link.set_group(self)
        self.first_link = link
        self.links.add(link)

    def update(self, board):
        self.links.clear()
        self.links.add(self.first_link)
        self.liberties.clear()
        self.first_link.find_adjacent(self.links, self.liberties, board)

    def add_link(self, link: StoneLink):
        link.set_group(self)
        self.links.add(link)

    def get_liberties(self):
        return len(self.liberties)

    def get_links(self):
        return self.links

    def merge(self, group):
        self.links = group.links | self.links
        self.liberties = group.liberties | self.liberties

    def set_links_group(self):
        for link in self.links:
            link.set_group(self)

    def count_stones(self):
        return len(self.links)

    def remove_stone_from_board(self, stone_link):
        stone_link.set_stone(Stone.NONE)
        stone_link.set_group(None)
        self.links.remove(stone_link)

    def capture_stones(self):
        for link in self.links:
            link.set_stone(Stone.NONE)
            link.set_group(None)

    def replace_captured_stones(self):
        for link in self.links:
            link.set_stone(self.stone)
            link.set_group(self)


class GroupOfStonesCollection:

    def __init__(self):
        self.groups = set()
        self.dead_stone_count = 0
        self.chain_of_commands = ChainOfCommands()

    def add_stone_link(self, stone_link: StoneLink, board):
        adjacent_stones = list(stone_link.get_adjacent_stones(board))
        adjacent_groups = set()
        for adjacent_stone in adjacent_stones:
            adjacent_groups.add(adjacent_stone.group)
        group = self.add_stone_link_to_group_of_stones(stone_link, adjacent_stones)
        self.update_groups_of_stones(board, adjacent_groups)
        dead_stones = self.find_dead_stones(group)
        self.dead_stone_count = self.count_dead_stones(dead_stones)
        if not self.has_dead_stones() and group.get_liberties() == 0:
            self.chain_of_commands.undo()
            raise ValidationError("Self capture is illegal")
        else:
            self.remove_dead_stones(dead_stones)
            return True

    def update_groups_of_stones(self, board, groups=None):
        groups = groups or self.groups
        for group in groups:
            group.update(board)

    def add_stone_link_to_group_of_stones(self, stone_link, adjacent_stones):
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

    def rollback(self):
        self.chain_of_commands.undo()
        self.chain_of_commands.undo()

    def reset(self):
        self.groups = set()
        self.dead_stone_count = 0
        self.chain_of_commands.reset()


class Turn:

    def __init__(self):
        self.turn = 1

    def next_turn(self):
        self.turn += 1

    def get_turn(self):
        return self.turn

    def current_player(self):
        return 1 if self.turn % 2 else 0

    def __str__(self):
        return 'Turn %d' % self.turn

    def reset(self):
        self.turn = 1

    def rollback_turn(self):
        self.turn -= 1


class MoveLog:

    def __init__(self):
        self.moves = []
        self.count = 0

    def add(self, move):
        self.moves.append(move)
        self.count += 1

    def pop(self):
        self.count -= 1
        return self.moves.pop()

    def count(self):
        return self.count

    def reset(self):
        self.moves = []
        self.count = 0


class BoardStack:

    def __init__(self):
        self.past_board_states = []

    def push(self, board):
        self.past_board_states.append(str(board))
        if len(self.past_board_states) > 2:
            del self.past_board_states[0]

    def breaks_simple_ko_rule(self, current_board):
        if len(self.past_board_states) < 2:
            return False
        return str(current_board) == self.past_board_states[-2]

    def reset(self):
        self.past_board_states = []

    def remove_last(self):
        if len(self.past_board_states):
            del self.past_board_states[-1]


class MoveValidation:
    @staticmethod
    def check_stone_link_is_empty(stone_link):
        if stone_link.stone != Stone.NONE:
            raise ValidationError('Stone cannot be placed on another stone')

    @staticmethod
    def check_point_is_in_bounds(point, size):
        if point.x < 0 or point.x > size[0] - 1 or point.y > size[1] - 1 or point.y < 0:
            raise ValidationError('Stone placed out of bounds')


class Board:
    def __init__(self, size: tuple):
        self.size = size
        self.board = self.make_board()
        self.group_collection = GroupOfStonesCollection()
        self.valid_move = False
        self.board_stack = BoardStack()

    def get_size(self):
        return self.size

    def get_point_stone_link(self, x, y):
        return self.board[y][x]

    def is_valid_move(self):
        return self.valid_move

    def draw(self):
        print(self)

    def in_grid(self, point):
        return point['x'] in range(self.size[0]) and point['y'] in range(self.size[1])

    def place_stone(self, point: Point, stone: Stone):
        MoveValidation.check_point_is_in_bounds(point, self.size)
        MoveValidation.check_stone_link_is_empty(self.get_point_stone_link(point.x, point.y))
        stone_link = self.get_point_stone_link(point.x, point.y)
        stone_link.set_stone(stone)
        self.valid_move = self.group_collection.add_stone_link(stone_link, self)
        if self.board_stack.breaks_simple_ko_rule(self):
            self.valid_move = False
            self.group_collection.chain_of_commands.undo()
            self.group_collection.chain_of_commands.undo()
            raise ValidationError('Breaks simple Ko Rule')
        else:
            self.board_stack.push(self)

    def reset(self):
        self.group_collection.reset()
        self.board_stack.reset()
        self.board = self.make_board()

    def make_board(self):
        return [[StoneLink(Point(x, y), Stone.NONE) for x in range(self.size[0])] for y in range(self.size[1])]

    def rollback(self):
        self.board_stack.remove_last()
        self.group_collection.rollback()


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


class MovesFromSGF:

    def __init__(self, sgf):
        os.path.isfile(sgf)
        with open(sgf, 'r') as file:
            self.st = file.read().replace('\n', '')
        self.sgf_coordinates = []
        self.korschelt_coordinates = []
        self.extract_coordinates()

    def get_as_korschelt(self):
        return self.korschelt_coordinates

    def get_as_sgf(self):
        return self.sgf_coordinates

    def extract_coordinates(self):
        matches = self.find_moves_in_sgf()
        for match in matches:
            coordinate = match.groups()[0]
            self.sgf_coordinates.append(coordinate)
            self.korschelt_coordinates.append(self.sgf_to_korschelt(coordinate))

    def find_moves_in_sgf(self):
        return re.finditer(r";[BW]\[([a-z]{2})\]", self.st, re.MULTILINE)

    def sgf_to_korschelt(self, coordinate):
        column_value = ord(coordinate[0]) - ord('a')
        row_value = ord(coordinate[1]) - ord('a')
        column_key = ALPHA_KEY[column_value]
        row_key = row_value + 1
        return "%s%s" % (row_key, column_key)


class Go:
    def __init__(self, size: int, height: int = None):
        if size > 25 or height is not None and height > 25:
            raise ValidationError('Board must be less than 25 x 25')
        if height is not None:
            size = {"width": height, "height": size}
        else:
            size = {"width": size, "height": size}
        self.size = size
        self.height = height
        self._board = Board((size["width"], size["height"]))
        self.board = self.board_data()
        self.players = (Player('Black', Stone.BLACK), Player('White', Stone.WHITE))
        self._turn = Turn()
        self.turn = self.players_turn()
        self.move_log = MoveLog()
        self.passes = 0

    def handicap_stones(self, stones):
        if self._turn.get_turn() > 1:
            raise ValidationError('Handicap stones cannot be placed after first move has been taken')
        if self.size["width"] == 19 and self.size["height"] == 19:
            self.place_handicap_stones(stones, HANDICAP_19_X_19)
        elif self.size["width"] == 13 and self.size["height"] == 13:
            self.place_handicap_stones(stones, HANDICAP_13_X_13)
        elif self.size["width"] == 9 and self.size["height"] == 9:
            self.place_handicap_stones(stones, HANDICAP_9_X_9)
        else:
            raise ValidationError('Handicap stones can only be placed on 19x19, 13x13 and 9x9 boards')

    def place_handicap_stones(self, stones, handicap_stones):
        current_player = self.get_current_player()
        for i in range(stones):
            self.make_move(handicap_stones[i], current_player)
        self._turn.next_turn()
        self.turn = self.players_turn()

        self.board = self.board_data()

    def board_data(self):
        return list(reversed(list(map(lambda x: list(map(lambda y: str(y.stone), x)), self._board.board))))

    def draw(self):
        print(self._board)

    def move(self, *moves):
        for move in moves:
            if move == 'pass':
                self.pass_turn()
                return
            self.passes = 0
            current_player = self.get_current_player()
            self.make_move(move, current_player)
            if self._board.is_valid_move():
                current_player.update_killed_stone_count(self._board.group_collection.get_dead_stones_count())
                self.move_log.add(move)
                self._turn.next_turn()
                self.turn = self.players_turn()
        self.board = self.board_data()

    def make_move(self, coordinate, current_player):
        point = Point(coordinate=coordinate)
        stone = current_player.get_stone()
        self._board.place_stone(point, stone)

    def rollback(self, number_of_turns: int):
        for _ in range(number_of_turns):
            if self.move_log.count == 0:
                raise ValidationError("Too many rollbacks")
            if self.move_log.pop() != 'pass':
                self._board.group_collection.rollback()
            self._turn.rollback_turn()
            self.turn = self.players_turn()
        self.board = self.board_data()

    def get_current_player(self):
        return self.players[self._turn.current_player() - 1]

    def get_position(self, coordinate):
        point = Point(coordinate=coordinate)
        return self._board.get_point_stone_link(point.x, point.y).stone.value

    def pass_turn(self):
        self.passes += 1
        self.move_log.add('pass')
        if self.passes == 2:
            self.end_game()
        self._turn.next_turn()
        self.turn = self.players_turn()
        self.board = self.board_data()

    def players_turn(self):
        return 'black' if self._turn.get_turn() % 2 else 'white'

    def reset(self):
        self.passes = 0
        self._board.reset()
        self._turn.reset()
        self.move_log.reset()
        self.board = self.board_data()
        self.turn = self.players_turn()

    def end_game(self):
        print('End Game.')

    def replay_sgf(self, sgf):
        moves = MovesFromSGF(sgf).get_as_korschelt()
        self.move(*moves)
        return len(moves)


if __name__ == '__main__':
    game = Go(19)
    from os import walk

    sgfs = []
    for (dir_path, dir_names, file_names) in walk('./sgf'):
        sgfs.extend(file_names)
        break

    for sgf in sgfs:
        print(sgf)
        moves = MovesFromSGF('./sgf/' + sgf).get_as_korschelt()
        index = 0
        while index < len(moves):
            print(index)
            game.move(moves[index])
            print("Move: %s  | Index = %d" % (moves[index], index))
            if random() > 0.8 and index > 10:
                rollback = int(randint(3, 5))
                print("Rollback by: %d" % rollback)
                game.rollback(rollback)
                index -= (rollback - 1)
                print("Index = %d" % index)
                game.draw()
                continue
            index += 1
            game.draw()
        game.draw()
        game.reset()
    # game = Go(20, 8)
    # moves = ["6F", "4N", "5O", "3K", "2N", "5B", "5A", "3N", "4G", "1C", "2B", "7S", "4Q", "7A", "6E", "5E", "7T", "7Q", "4T", "1P", "6J", "7U", "3Q", "5M", "7F", "2A", "7J", "2U", "2S", "4S", "2R", "4P", "4F", "1E", "2T", "1R", "pass", "2H", "7E", "3E", "3T", "6C", "5U", "5G", "1J", "7C", "1A", "3S", "2O", "5J", "7N", "3F", "4J", "pass", "4A", "6D", "6M", "7H", "3M", "6N", "5K", "1G", "3O", "4L", "3P"]
    # for move in moves:
    #     try:
    #         game.move(move)
    #     except ValidationError:
    #         continue
    # game.rollback(len(moves))

    # from os import walk
    #
    # sgfs = []
    # for (dir_path, dir_names, file_names) in walk('./sgf'):
    #     sgfs.extend(file_names)
    #     break
    #
    # game = Go(19)
    #
    # for sgf in sgfs:
    #     print(sgf)
    #     move_count = game.replay_sgf('./sgf/%s' % sgf)
    #     game.draw()
    #     game.rollback(move_count)
    #     game.replay_sgf('./sgf/%s' % sgf)
    #     game.draw()
    #     game.reset()
    # #
    # game = Go(9)
    # move_count = game.replay_sgf('./sgf/test-one.sgf')
    # game.draw()
    # game.rollback(move_count)
    # game.replay_sgf('./sgf/test-one.sgf')
    # game.draw()
    # game.reset()

    # game = Go(9)
    # board_point = Point(coordinate='1A')
    # assert board_point.x == 0 and board_point.y == 0
    # board_point = Point(coordinate='9J')
    # assert board_point.x == 8 and board_point.y == 8
    # moves = ["4D", "3D", "4H", "5D", "3H", "4C", "5B", "4E"]
    # game.move(*moves)
    # print(game.board)
    # assert game.get_position('4D') == '.'
    # game.reset()
    # moves = ["6D", "7E", "6E", "6F", "4D", "5E", "5D", "7D",
    #          "5C", "6C", "7H", "3D", "4E", "4F", "3E", "2E",
    #          "3F", "3G", "2F", "1F", "2G", "2H", "1G", "1H",
    #          "4C", "3C", "6H", "4B", "5H", "5B"]
    # captured = ["6D", "6E", "4D", "5D", "5C", "4E", "3E", "3F", "2F", "2G", "1G", "4C"]
    # game.move(*moves)
    # for capture in captured:
    #     assert game.get_position(capture) == '.'
    # print(game.board)
    # game.reset()
    # moves = ["9A", "8A", "8B", "9B"]
    # game.move(*moves)
    # assert game.get_position('9A') == '.'
    # print(game.board)
    # game.reset()
    # moves = ["5D", "5E", "4E", "6E", "7D", "4F", "7E", "3E", "5F", "4D",
    #          "6F", "6D", "6C", "7F", "4E", "5E"]
    # captured = ["4E", "6D", "6E"]
    # game.move(*moves)
    # for capture in captured:
    #     assert game.get_position(capture) == '.'
    # print(game.board)
    # game.reset()
    # small_game = Go(5)
    # moves = ["5A", "1E", "5B", "2D", "5C", "2C", "3A",
    #          "1C", "2A", "3D", "2B", "3E", "4D", "4B",
    #          "4E", "4A", "3C", "3B", "1A", "4C", "3C"]
    # captured = ["4A", "4B", "4C", "3B"]
    # small_game.move(*moves)
    # for capture in captured:
    #     assert small_game.get_position(capture) == '.'
    # small_game.reset()
    # moves = ["2A", "5A", "1B", "5B", "3B", "5C", "2C", "2B", "5D"]
    # small_game.move(*moves)
    # assert small_game.get_position('2B') == '.'
    # assert small_game.get_position('5D') == 'o'
    # small_game.reset()
    # moves = ["2A", "1C", "1B", "2D", "3B", "3C", "2C", "2B", "2C", "5A"]
    # small_game.move(*moves)
    # print(small_game.board)
    # assert small_game.get_position('2B') == 'o'
    # assert small_game.get_position('2C') == '.'
    # assert small_game.get_position('5A') == 'x'
    # small_game.reset()
    # moves = ["5C", "5B", "4D", "4A", "3C", "3B", "2D", "2C", "4B", "4C", "4B", "2B"]
    # small_game.move(*moves)
    # print(small_game.board)
    # assert small_game.get_position("2B") == 'x'
    # assert small_game.get_position("4B") == '.'
    # small_game.reset()
    # moves = ["1A", "2A"]
    # small_game.move(*moves)
    # print(small_game.board)
    # small_game.rollback(1)
    # print(small_game.board)
    # assert small_game.get_position("1A") == 'x'
    # assert small_game.get_position("2A") == '.'
    # small_game.reset()
    # moves = ["1A", "2A", "1E", "1B"]
    # small_game.move(*moves)
    # print(small_game.board)
    # assert small_game.get_position("1A") == '.'
    # assert small_game.get_position("1B") == 'o'
    # small_game.rollback(1)
    # print(small_game.board)
    # assert small_game.get_position("1A") == 'x'
    # assert small_game.get_position("1B") == '.'
    # small_game.reset()
    # moves = ["1A", "2A", "1E", "1C"]
    # small_game.move(*moves)
    # print(small_game.board)
    # small_game.pass_turn()
    # moves = ["4B", "4C"]
    # small_game.move(*moves)
    # print(small_game.board)
    # assert small_game.get_position("1C") == 'o'
    # assert small_game.get_position("4B") == 'o'
    # assert small_game.get_position("4C") == 'x'
    # small_game.rollback(3)
    # print(small_game.board)
    # assert small_game.get_position("1C") == 'o'
    # assert small_game.get_position("4B") == '.'
    # assert small_game.get_position("4C") == '.'
