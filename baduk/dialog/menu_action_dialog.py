from baduk.action.start_game import StartGameAction
from baduk.ui.action.action_collection import ActionCollection
from baduk.ui.action.action_item import ActionItem


class MenuActionDialog:

    @staticmethod
    def main_menu():
        return ActionCollection(
            ActionItem('p', 'Play Game', StartGameAction()),
            ActionItem('q', 'Quit Game'),
        )
