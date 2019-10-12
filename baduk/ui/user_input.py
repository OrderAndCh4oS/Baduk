# coding=utf-8


class UserInput:

    @staticmethod
    def get_input(*args, **kwargs):
        player_input = input(*args, **kwargs)
        return player_input
