from baduk.constants.constants import ALPHA_KEY
from baduk.ui.action.action_collection import ActionCollection
from baduk.ui.action.action_item import ActionItem


class PlayerActionDialog:

    def __init__(self, size):
        self.keys = ["%s%s" % (i + 1, ALPHA_KEY[j]) for i in range(size) for j in range(size)]

    def player_turn(self):
        return ActionCollection(
            ActionItem(self.keys, 'Enter Move'),
            ActionItem('p', 'Pass'),
            ActionItem('u', 'Undo'),
        )
