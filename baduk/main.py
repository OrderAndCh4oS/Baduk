from baduk.constants import ALPHA_KEY
from baduk.enums import Stone
from baduk.exceptions import ValidationError
from baduk.player import Player
from baduk.point import Point
from baduk.turn import Turn


class GroupLink:
    group = None

    def __init__(self, point, stone):
        self.point = point
        self.stone = stone

    def __repr__(self):
        return '%s: %s' % (str(self.point), str(self.stone))

    def set_group(self, group):
        self.group = group

    def set_stone(self, stone):
        self.stone = stone

    def get_adjacent_stones(self, board):
        return self.point.filter_adjacent_links(
            lambda adjacent_link: self.stone == adjacent_link.stone,
            board
        )

    def update(self, links, liberties, board):
        for adjacent_point in self.point.adjacent_points():
            if board.in_grid(adjacent_point):
                adjacent_link = board.get_point_group_link(**adjacent_point)
                self.set_links_and_liberties(adjacent_link, board, liberties, links)

    def set_links_and_liberties(self, adjacent_link, board, liberties, links):
        if adjacent_link.stone == self.stone and adjacent_link not in links:
            links.add(adjacent_link)
            adjacent_link.update(links, liberties, board)
        elif adjacent_link.stone == Stone.NONE:
            liberties.add(adjacent_link)


class Group:
    def __init__(self, link: GroupLink):
        self.links = set()
        self.liberties = set()
        link.set_group(self)
        self.first_link = link
        self.links.add(link)

    def __repr__(self):
        return 'Key: %s | Liberties %d' % (
            (', '.join([str(link) for link in self.links])), len(self.liberties))

    def add_link(self, link: GroupLink):
        link.set_group(self)
        self.first_link = link
        self.links.add(link)

    def get_liberties(self):
        return len(self.liberties)

    def get_links(self):
        return self.links

    def update(self, board):
        self.links = {self.first_link}
        self.liberties = set()
        self.first_link.update(self.links, self.liberties, board)

    def combine(self, group):
        self.links = group.links | self.links
        self.liberties = group.liberties | self.liberties

    def update_links(self):
        for link in self.links:
            link.set_group(self)

    def count_stones(self):
        return len(self.links)

    def remove_stones(self):
        for link in self.links:
            link.set_stone(Stone.NONE)
            link.set_group(None)


class GroupCollection:
    groups = set()
    dead_stones = set()

    def update(self, board):
        for group in self.groups:
            group.update(board)

    # Todo: update should not need to return anything
    def add_stone(self, group_link: GroupLink, board):
        adjacent_stones = list(group_link.get_adjacent_stones(board))
        if len(adjacent_stones) > 1:
            group = self.combine_groups_adjacent_to_link(adjacent_stones, group_link)
        elif len(adjacent_stones) == 1:
            group = self.add_link_adjacent_group(adjacent_stones, group_link)
        else:
            group = self.create_new_group(group_link)
        self.update(board)
        return group

    def create_new_group(self, group_link: GroupLink):
        group = Group(group_link)
        self.groups.add(group)
        return group

    def add_link_adjacent_group(self, adjacent_stones, group_link: GroupLink):
        adjacent_stone = adjacent_stones[0]
        group = adjacent_stone.group
        group.add_link(group_link)
        return group

    def combine_groups_adjacent_to_link(self, adjacent_stones: list, group_link: GroupLink):
        group = Group(group_link)
        old_groups = set()
        for adjacent_stone in adjacent_stones:
            old_groups.add(adjacent_stone.group)
            group.combine(adjacent_stone.group)
        for old_group in old_groups:
            self.groups.remove(old_group)
        group.update_links()
        self.groups.add(group)
        return group

    def remove_dead_stones(self):
        if len(self.dead_stones) > 0:
            for dead_stones in self.dead_stones:
                dead_stones.remove_stones()
                self.groups.remove(dead_stones)
        self.dead_stones = set()

    def find_dead_stones(self, current_group, board):
        for group in self.groups:
            # Todo: for class instance comparison classes should implement __hash__ and/or __eq__
            if group.get_liberties() == 0 and str(group) != str(current_group):
                self.dead_stones.add(group)

    def get_dead_stones_count(self):
        count = 0
        for dead_stones in self.dead_stones:
            count += len(dead_stones.get_links()) if dead_stones else 0
        return count

    def has_dead_stones(self):
        return True if len(self.dead_stones) else False


class Board:

    def __init__(self, size: tuple):
        self.size = size
        self.board = self.make_board()
        self.group_collection = GroupCollection()

    def __repr__(self):
        alpha_row = ' '.join([ALPHA_KEY[i] for i in range(self.size[0])])
        rows = '\n'.join(['%s %s' % (i + 1, row) for i, row in
                          enumerate(map(lambda x: ' '.join(map(lambda y: str(y.stone), x)), self.board))])
        return '  %s\n%s' % (alpha_row, rows)

    def get_size(self):
        return self.size

    def get_point_group_link(self, x, y):
        return self.board[y][x]

    def draw(self):
        print(self)

    def in_grid(self, point):
        return point['x'] in range(self.size[0]) and point['y'] in range(self.size[1])

    def place_stone(self, point: Point, stone: Stone):
        self.check_point_is_in_bounds(point)
        self.check_point_is_empty(point)
        group_link = self.get_point_group_link(point.x, point.y)
        group_link.set_stone(stone)
        group = self.group_collection.add_stone(group_link, self)
        self.group_collection.find_dead_stones(group, self)
        self.draw()
        if not self.group_collection.has_dead_stones() and group.get_liberties() == 0:
            group_link.stone = Stone.NONE
            return False
        else:
            self.group_collection.remove_dead_stones()
            return True

    def check_point_is_empty(self, point):
        if self.get_point_group_link(point.x, point.y).stone != Stone.NONE:
            raise ValidationError('Stone cannot be placed on another stone')

    def check_point_is_in_bounds(self, point):
        if point.x < 0 or point.x > self.size[0] - 1 or point.y > self.size[1] - 1 or point.y < 0:
            raise ValidationError('Stone placed out of bounds')

    def reset(self):
        self.group_collection = GroupCollection()
        self.board = self.make_board()

    def make_board(self):
        return [[GroupLink(Point(x, y), Stone.NONE) for x in range(self.size[0])] for y in range(self.size[1])]


class Baduk:
    passes = 0

    def __init__(self, size: int, height: int = None):
        if size > 25 or height is not None and height > 25:
            raise ValidationError('Board must be less than 25 x 25')
        if height is not None:
            size = (size, height)
        else:
            size = (size, size)
        self._board = Board(size)
        self.size = size
        self.turn = Turn()
        self.players = (Player('Black', Stone.BLACK), Player('White', Stone.WHITE))

    def board(self):
        self._board.draw()

    def move(self, *coordinates):
        for coordinate in coordinates:
            self.passes = 0
            current_player = self.get_current_player()
            point = Point(coordinate=coordinate)
            stone = current_player.get_stone()
            print(point, stone)
            self._board.place_stone(point, stone)
            current_player.update_killed_stone_count(self._board.group_collection.get_dead_stones_count())
            self.turn.next_turn()
            self.board()

    def make_move(self, point, stone):
        self._board.place_stone(point, stone)

    def get_current_player(self):
        return self.players[self.turn.current_player()]

    def get_position(self, coordinate):
        point = Point(coordinate=coordinate)
        return self._board.get_point_group_link(point.x, point.y).stone.value

    def pass_turn(self):
        self.passes += 1
        if self.passes == 2:
            self.end_game()
        self.turn.next_turn()

    def reset(self):
        self._board.reset()
        self.turn.reset()

    def end_game(self):
        print('End Game.')


if __name__ == '__main__':
    game = Baduk(9)
    point = Point(coordinate='1A')
    assert point.x == 0 and point.y == 0
    point = Point(coordinate='9J')
    assert point.x == 8 and point.y == 8
    moves = ["4D", "3D", "4H", "5D", "3H", "4C", "5B", "4E"]
    game.move(*moves)
    game.board()
    assert game.get_position('4D') == '.'
    game.reset()
    moves = ["6D", "7E", "6E", "6F", "4D", "5E", "5D", "7D",
             "5C", "6C", "7H", "3D", "4E", "4F", "3E", "2E",
             "3F", "3G", "2F", "1F", "2G", "2H", "1G", "1H",
             "4C", "3C", "6H", "4B", "5H", "5B"]
    captured = ["6D", "6E", "4D", "5D", "5C", "4E", "3E", "3F", "2F", "2G", "1G", "4C"]
    game.move(*moves)
    for capture in captured:
        assert game.get_position(capture) == '.'
    game.board()
    game.reset()
    moves = ["9A", "8A", "8B", "9B"]
    game.move(*moves)
    assert game.get_position('9A') == '.'
    game.board()
    game.reset()
    moves = ["5D", "5E", "4E", "6E", "7D", "4F", "7E", "3E", "5F", "4D",
             "6F", "6D", "6C", "7F", "4E", "5E"]
    captured = ["4E", "6D", "6E"]
    game.move(*moves)
    for capture in captured:
        assert game.get_position(capture) == '.'
    game.board()
    game.reset()
    small_game = Baduk(5)
    moves = ["5A", "1E", "5B", "2D", "5C", "2C", "3A",
             "1C", "2A", "3D", "2B", "3E", "4D", "4B",
             "4E", "4A", "3C", "3B", "1A", "4C", "3C"]
    captured = ["4A", "4B", "4C", "3B"]
    small_game.move(*moves)
    for capture in captured:
        assert small_game.get_position(capture) == '.'
