from baduk.dialog.board_set_up_dialog import BoardSetUpDialog
from baduk.dialog.player_action_dialog import PlayerActionDialog
from baduk.exception.exceptions import ValidationError
from baduk.game.game import Game
from baduk.ui.action.action import Action
from baduk.ui.user_menu import UserMenu
from baduk.ui.view import View


class StartGameAction(Action):

    def execute(self, input_value):
        size = int(UserMenu(BoardSetUpDialog.select_board_size(), "Select Board Size")())
        game = Game(size)
        if size in [9, 13, 19]:
            handicap = UserMenu(BoardSetUpDialog.set_handicap(), "Set Handicap")()
            game.handicap(int(handicap))
        game.board()
        player_dialog = PlayerActionDialog(size)
        passes = 0
        while passes < 2:
            move = UserMenu(player_dialog.player_turn(), "Place Stone")()
            if move == 'p':
                passes += 1
                game.board()
            elif move == 'u':
                game.rollback(1)
                game.board()
            else:
                passes = 0
                try:
                    game.move(move)
                    game.board()
                except ValidationError as error:
                    game.board()
                    View("error.txt").render(error=error)
