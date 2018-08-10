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

    def find_adjacent(self, board):
        adjacent_links = self.point.filter_adjacent_links(
            lambda adjacent_link: self.stone == adjacent_link.stone,
            board
        )
        print([str(link) for link in adjacent_links])

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
        self.first_link = link
        self.liberties = set()
        self.links = set()
        self.links.add(link)

    def __repr__(self):
        return 'Stone Coordinates: %s, Liberties %d' % (
        (', '.join([str(link) for link in self.links])), len(self.liberties))

    def get_links(self, board):
        self.first_link.find_liberties(self.links, self.liberties, board)
        return self.liberties


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
        print(group_link.find_adjacent(self))
        group = Group(group_link)
        links = group.get_links(self)
        print(group)


class Baduk:

    def __init__(self, size: int):
        self._board = Board(size)
        self.turn = Turn()
        self.players = (Player('Black', Stone.BLACK), Player('White', Stone.WHITE))

    def board(self):
        self._board.draw()

    def move(self, coordinate):
        point = Point(coordinate=coordinate)
        stone = self.players[self.turn.current_player()].get_stone()
        self._board.place_stone(point, stone)
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
    baduk.move('4C')
    baduk.board()
    baduk.move('3C')
    baduk.board()
    baduk.move('4B')
    baduk.board()
    baduk.move('5D')
    baduk.board()
