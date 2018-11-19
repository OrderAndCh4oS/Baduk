from baduk.constants.constants import ALPHA_KEY
from baduk.enums.enums import Stone
from baduk.game.board_stack import BoardStack
from baduk.game.point import Point
from baduk.stones.group_of_stones_collection import GroupOfStonesCollection
from baduk.stones.stone_link import StoneLink
from baduk.validation.move_validation import MoveValidation


class Board:
    def __init__(self, size: tuple):
        self.size = size
        self.board = self.make_board()
        self.group_collection = GroupOfStonesCollection()
        self.valid_move = False
        self.board_stack = BoardStack()

    def __repr__(self):
        return '\n'.join([row for row in map(lambda x: ' '.join(map(lambda y: y.stone.value, x)), self.board)])

    def get_size(self):
        return self.size

    def get_point_stone_link(self, x, y):
        return self.board[y][x]

    def is_valid_move(self):
        return self.valid_move

    def draw(self):
        alpha_row = ' '.join([str(ALPHA_KEY[i]) for i in range(self.size[0])])
        rows = '\n'.join(['%02s %s' % (i + 1, row) for i, row in
                          enumerate(map(lambda x: ' '.join(map(lambda y: y.stone.value, x)), self.board))])
        print('   %s\n%s' % (alpha_row, rows))

    def in_grid(self, point):
        return 0 <= point['x'] < self.size[0] and 0 <= point['y'] < self.size[1]

    def place_stone(self, point: Point, stone: Stone):
        MoveValidation.check_point_is_in_bounds(point, self.size)
        MoveValidation.check_stone_link_is_empty(self.get_point_stone_link(point.x, point.y))
        stone_link = self.get_point_stone_link(point.x, point.y)
        stone_link.set_stone(stone)
        self.group_collection.add_stone_link(stone_link, self)
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
        self.group_collection.update_groups_of_stones(self)
