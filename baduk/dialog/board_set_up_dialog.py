from baduk.ui.action.action_collection import ActionCollection
from baduk.ui.action.action_item import ActionItem


class BoardSetUpDialog:

    @staticmethod
    def select_board_size():
        return ActionCollection(
            ActionItem(range(5, 26), 'Select Board Size'),
        )

    @staticmethod
    def set_handicap():
        return ActionCollection(
            ActionItem(range(0, 10), 'Set Handicap'),
        )
