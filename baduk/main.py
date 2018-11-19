from baduk.dialog.menu_action_dialog import MenuActionDialog
from baduk.ui.user_menu import UserMenu


class Main:

    def __init__(self):
        UserMenu(MenuActionDialog.main_menu())()


if __name__ == '__main__':
    Main()
