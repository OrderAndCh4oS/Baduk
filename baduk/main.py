from baduk.enums import Stone
from baduk.exceptions import ValidationError
from baduk.game.board import Board
from baduk.game.player import Player
from baduk.game.point import Point
from baduk.game.turn import Turn


class DeadStoneCollection:
    pass


class Baduk:

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
        self.passes = 0
        self.previous_boards = []

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
            if self._board.is_valid_move():
                current_player.update_killed_stone_count(self._board.group_collection.get_dead_stones_count())
                self.turn.next_turn()
                self.board()

    def make_move(self, point, stone):
        self._board.place_stone(point, stone)

    def get_current_player(self):
        return self.players[self.turn.current_player()]

    def get_position(self, coordinate):
        point = Point(coordinate=coordinate)
        return self._board.get_point_stone_link(point.x, point.y).stone.value

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
    # game = Baduk(9)
    # board_point = Point(coordinate='1A')
    # assert board_point.x == 0 and board_point.y == 0
    # board_point = Point(coordinate='9J')
    # assert board_point.x == 8 and board_point.y == 8
    # moves = ["4D", "3D", "4H", "5D", "3H", "4C", "5B", "4E"]
    # game.move(*moves)
    # game.board()
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
    # game.board()
    # game.reset()
    # moves = ["9A", "8A", "8B", "9B"]
    # game.move(*moves)
    # assert game.get_position('9A') == '.'
    # game.board()
    # game.reset()
    # moves = ["5D", "5E", "4E", "6E", "7D", "4F", "7E", "3E", "5F", "4D",
    #          "6F", "6D", "6C", "7F", "4E", "5E"]
    # captured = ["4E", "6D", "6E"]
    # game.move(*moves)
    # for capture in captured:
    #     assert game.get_position(capture) == '.'
    # game.board()
    # game.reset()
    small_game = Baduk(5)
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
    # assert small_game.get_position('5D') == 'x'
    small_game.reset()
    small_game.reset()
    moves = ["2A", "1C", "1B", "2D", "3B", "3C", "2C", "2B", "2C", "5A"]
    small_game.move(*moves)
    small_game.board()
    assert small_game.get_position('2B') == 'x'
    assert small_game.get_position('2C') == '.'
    assert small_game.get_position('5A') == 'o'
