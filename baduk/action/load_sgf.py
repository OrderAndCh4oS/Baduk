from os import walk

from ansi_colours import AnsiColours as Colour

from baduk.exception.exceptions import ValidationError
from baduk.game.game import Game
from baduk.service.move_from_sgf import MovesFromSGF
from baduk.ui.action.action import Action
from baduk.ui.pagination import Pagination
from baduk.ui.user_input import UserInput
from baduk.ui.view import View


def move(game, *coordinate):
    try:
        game.move(*coordinate)
        game.board()
    except ValidationError as error:
        game.board()
        View("error.txt").render(error=error)


def rollback(game, number):
    try:
        game.rollback(number)
        game.board()
    except ValidationError as error:
        game.board()
        View("error.txt").render(error=error)


class LoadSGFAction(Action):
    def execute(self, input_value):

        sgfs = []
        for (dir_path, dir_names, file_names) in walk('../sgf'):
            sgfs.extend([[i + 1, file_name] for i, file_name in enumerate(file_names)])
            break
        sgf = Pagination(sgfs, ['key', 'files'])()
        if not sgf:
            return True

        moves = MovesFromSGF('../sgf/' + sgf[1]).get_as_korschelt()
        game = Game(19)
        game.board()
        index = 0
        while index < len(moves):
            user_input = ''
            while user_input not in ['<<', '<', '>', '>>', 'b']:
                user_input = UserInput.get_input('\n%s | %s | %s | %s\n%s Back\n' % (
                    Colour.green("<<"),
                    Colour.green("<"),
                    Colour.green(">"),
                    Colour.green(">>"),
                    Colour.green("b")
                ))
            if user_input == '>':
                move(game, moves[index])
                print("Move: ", moves[index])
                index += 1
                print("Turn: ", index + 1)
                continue
            elif user_input == '>>':
                move(game, *moves[index:index + 10])
                print("Move: ", ", ".join(moves[index:index + 10]))
                index += 10
                print("Turn: ", index + 1)
                continue
            elif user_input == '<':
                index -= 1
                rollback(game, 1)
                print("Turn: ", index + 1)
                continue
            elif user_input == '<<':
                index -= 10
                rollback(game, 10)
                print("Turn: ", index + 1)
                continue
            elif user_input == 'b':
                break
            game.board()
        game.reset()
