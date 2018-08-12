from baduk.constants import HANDICAP_9_X_9, HANDICAP_13_X_13, HANDICAP_19_X_19
from baduk.exceptions import ValidationError
from baduk.game.board import Board
from baduk.game.player import Player
from baduk.game.point import Point
from baduk.game.turn import Turn
from baduk.stones.enums import Stone


class DeadStoneCollection:
    pass


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


class Baduk:

    def __init__(self, size: int, height: int = None):
        if size > 25 or height is not None and height > 25:
            raise ValidationError('Board must be less than 25 x 25')
        if height is not None:
            size = (size, height)
        else:
            size = (size, size)
        self.size = size
        self.height = height
        self._board = Board(size)
        self.players = (Player('Black', Stone.BLACK), Player('White', Stone.WHITE))
        self._turn = Turn()
        self.move_log = MoveLog()
        self.passes = 0

    def handicap(self, stones):
        if self._turn.get_turn() > 1:
            raise ValidationError('Handicap stones cannot be placed after first move has been taken')
        if self.size[0] == 19 and self.size[1] == 19:
            self.place_handicap_stones(stones, HANDICAP_19_X_19)
        elif self.size[0] == 13 and self.size[1] == 13:
            self.place_handicap_stones(stones, HANDICAP_13_X_13)
        elif self.size[0] == 9 and self.size[1] == 9:
            self.place_handicap_stones(stones, HANDICAP_9_X_9)
        else:
            raise ValidationError('Handicap stones can only be placed on 19x19, 13x13 and 9x9 boards')

    def place_handicap_stones(self, stones, handicap_stones):
        current_player = self.get_current_player()
        for i in range(stones):
            self.make_move(handicap_stones[i], current_player)
        self._turn.next_turn()

    def board(self):
        self._board.draw()

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

    def make_move(self, coordinate, current_player):
        point = Point(coordinate=coordinate)
        stone = current_player.get_stone()
        self._board.place_stone(point, stone)

    def rollback(self, number_of_turns: int):
        for _ in range(number_of_turns):
            if self.move_log.count == 0:
                return
            if self.move_log.pop() != 'pass':
                self._board.group_collection.rollback_turn()
            self._turn.rollback_turn()

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

    def turn(self):
        return 'black' if self._turn.get_turn() % 2 else 'white'

    def reset(self):
        self.passes = 0
        self._board.reset()
        self._turn.reset()
        self.move_log.reset()

    def end_game(self):
        print('End Game.')


if __name__ == '__main__':
    game = Baduk(9)
    board_point = Point(coordinate='1A')
    assert board_point.x == 0 and board_point.y == 0
    board_point = Point(coordinate='9J')
    assert board_point.x == 8 and board_point.y == 8
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
    small_game.reset()
    moves = ["2A", "5A", "1B", "5B", "3B", "5C", "2C", "2B", "5D"]
    small_game.move(*moves)
    assert small_game.get_position('2B') == '.'
    assert small_game.get_position('5D') == 'o'
    small_game.reset()
    moves = ["2A", "1C", "1B", "2D", "3B", "3C", "2C", "2B", "2C", "5A"]
    small_game.move(*moves)
    small_game.board()
    assert small_game.get_position('2B') == 'o'
    assert small_game.get_position('2C') == '.'
    assert small_game.get_position('5A') == 'x'
    small_game.reset()
    moves = ["5C", "5B", "4D", "4A", "3C", "3B", "2D", "2C", "4B", "4C", "4B", "2B"]
    small_game.move(*moves)
    small_game.board()
    assert small_game.get_position("2B") == 'x'
    assert small_game.get_position("4B") == '.'
    small_game.reset()
    moves = ["1A", "2A"]
    small_game.move(*moves)
    small_game.board()
    small_game.rollback(1)
    small_game.board()
    assert small_game.get_position("1A") == 'x'
    assert small_game.get_position("2A") == '.'
    small_game.reset()
    moves = ["1A", "2A", "1E", "1B"]
    small_game.move(*moves)
    small_game.board()
    assert small_game.get_position("1A") == '.'
    assert small_game.get_position("1B") == 'o'
    small_game.rollback(1)
    small_game.board()
    assert small_game.get_position("1A") == 'x'
    assert small_game.get_position("1B") == '.'
    small_game.reset()
    moves = ["1A", "2A", "1E", "1C"]
    small_game.move(*moves)
    small_game.board()
    small_game.pass_turn()
    moves = ["4B", "4C"]
    small_game.move(*moves)
    small_game.board()
    assert small_game.get_position("1C") == 'o'
    assert small_game.get_position("4B") == 'o'
    assert small_game.get_position("4C") == 'x'
    small_game.rollback(3)
    small_game.board()
    assert small_game.get_position("1C") == 'o'
    assert small_game.get_position("4B") == '.'
    assert small_game.get_position("4C") == '.'
