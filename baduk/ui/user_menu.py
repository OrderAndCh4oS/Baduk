from ansi_colours import AnsiColours as Colour

from baduk.ui.action.action_collection import ActionCollection
from baduk.ui.user_input import UserInput
from baduk.ui.view import View


class UserMenu:

    def __init__(self, action_collection: ActionCollection, title="Menu"):
        self.action_collection = action_collection
        self.title = title

    def __call__(self):
        user_input = None
        keys = {}
        View("menu.txt").render(title=self.title, menu=self._prepare_menu(keys))
        while user_input not in keys:
            user_input = UserInput.get_input('Select an option: ')
        return keys[user_input](user_input)

    def _prepare_menu(self, keys):
        menu = ''
        for action in self.action_collection.actions:
            if isinstance(action.key, range):
                menu += "%s: %d-%d\n" % (str(action), action.key[0], action.key[-1])
                keys.update({str(key): action.execute for key in action.key})
            elif isinstance(action.key, list):
                menu += "%s: %s-%s\n" % (str(action), action.key[0], action.key[-1])
                keys.update({str(key): action.execute for key in action.key})
            else:
                menu += "%s: %s\n" % (str(action), Colour.green(action.key))
                keys[str(action.key)] = action.execute
        return menu
