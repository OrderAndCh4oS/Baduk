from baduk.constants import ALPHA_KEY
from baduk.enums import Stone
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

    def find_liberties(self, links, liberties, board):
        for adjacent_point in self.point.adjacent_points():
            if board.in_grid(adjacent_point):
                adjacent_link = board.get_point(**adjacent_point)
                self.set_links_and_liberties(adjacent_link, board, liberties, links)

    def set_links_and_liberties(self, adjacent_link, board, liberties, links):
        if adjacent_link.stone == self.stone and adjacent_link not in links:
            links.add(adjacent_link)
            adjacent_link.find_liberties(links, liberties, board)
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
        return 'Stone Coordinates: %s | Liberties %d' % (
        (', '.join([str(link) for link in self.links])), len(self.liberties))

    def add_link(self, link):
        link.set_group(self)
        self.first_link = link
        self.links.add(link)

    def get_liberties(self, board):
        self.links = set()
        self.liberties = set()
        self.first_link.find_liberties(self.links, self.liberties, board)
        return len(self.liberties)

    def combine(self, group):
        self.links = group.links | self.links
        self.liberties = group.liberties | self.liberties
        for link in self.links:
            link.set_group(self)

    def count_stones(self):
        return len(self.links)

    def remove_stones(self):
        for link in self.links:
            link.set_stone(Stone.NONE)
            link.set_group(None)

class Board:
    groups = []

    def __init__(self, size: int):
        self.size = size
        self.board = [[GroupLink(Point(x, y), Stone.NONE) for x in range(size)] for y in range(size)]

    def __repr__(self):
        alpha_row = ' '.join([ALPHA_KEY[i] for i in range(self.size)])
        rows = '\n'.join(['%s %s' % (i + 1, row) for i, row in
                          enumerate(map(lambda x: ' '.join(map(lambda y: str(y.stone), x)), self.board))])
        return '  %s\n%s' % (alpha_row, rows)

    def get_size(self):
        return self.size

    def get_point(self, x, y):
        return self.board[y][x]

    def draw(self):
        print(self)

    def in_grid(self, point):
        return point['x'] in range(self.size) and point['y'] in range(self.size)

    def place_stone(self, point: Point, stone: Stone):
        group_link = self.get_point(point.x, point.y)
        group_link.stone = stone
        self.update_groups(group_link)

    def update_groups(self, group_link):
        adjacent_stones = group_link.get_adjacent_stones(self)
        if len(list(adjacent_stones)) > 1:
            group = self.combine_groups_adjacent_to_link(adjacent_stones, group_link)
        elif len(list(adjacent_stones)) == 1:
            group = self.add_link_adjacent_group(adjacent_stones, group_link)
        else:
            group = self.create_new_group(group_link)
        group.get_liberties(self)
        print([str(group) for group in self.groups])

    def create_new_group(self, group_link):
        group = Group(group_link)
        self.groups.append(group)
        return group

    def add_link_adjacent_group(self, adjacent_stones, group_link):
        adjacent_stone = adjacent_stones[0]
        group = adjacent_stone.group
        group.add_link(group_link)
        return group

    def combine_groups_adjacent_to_link(self, adjacent_stones, group_link):
        group = Group(group_link)
        for adjacent_stone in adjacent_stones:
            self.groups.remove(adjacent_stone.group)
            group.combine(adjacent_stone.group)
            del adjacent_stone.group
            self.groups.append(group)
        return group

    def count_dead_stones(self):
        dead_stones = 0
        for group in self.groups:
            liberties = group.get_liberties(self)
            print(liberties)
            if liberties == 0:
                dead_stones = group.count_stones()
                group.remove_stones()
                self.groups.remove(group)
                break
        return dead_stones

class Baduk:

    def __init__(self, size: int):
        self._board = Board(size)
        self.turn = Turn()
        self.players = (Player('Black', Stone.BLACK), Player('White', Stone.WHITE))

    def board(self):
        self._board.draw()

    def move(self, coordinate):
        current_player =  self.players[self.turn.current_player()]
        point = Point(coordinate=coordinate)
        stone = current_player.get_stone()
        self._board.place_stone(point, stone)
        current_player.update_killed_stone_count(self._board.count_dead_stones())
        self.turn.next_turn()


if __name__ == '__main__':
    baduk = Baduk(9)
    baduk.board()
    point = Point(coordinate='1A')
    assert point.x == 0 and point.y == 0
    point = Point(coordinate='9J')
    assert point.x == 8 and point.y == 8
    baduk.move('4D')
    baduk.board()
    baduk.move('5D')
    baduk.board()
    baduk.move('5E')
    baduk.board()
    baduk.move('1A')
    baduk.board()
    baduk.move('5C')
    baduk.board()
    baduk.move('6D')
    baduk.board()
    baduk.move('7D')
    baduk.board()
    baduk.move('2A')
    baduk.board()
    baduk.move('6C')
    baduk.board()
    baduk.move('3A')
    baduk.board()
    baduk.move('6E')
    baduk.board()
