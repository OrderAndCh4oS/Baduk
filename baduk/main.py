#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from baduk.dialog.menu_action_dialog import MenuActionDialog
from baduk.ui.user_menu import UserMenu


class Main:
    def __init__(self):
        while True:
            if UserMenu(MenuActionDialog.main_menu())() == 'q':
                break


if __name__ == '__main__':
    Main()
