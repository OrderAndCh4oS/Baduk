class Turn:

    def __init__(self):
        self.turn = 1

    def next_turn(self):
        self.turn += 1

    def get_turn(self):
        return self.turn

    def current_player(self):
        return 1 if self.turn % 2 else 0

    def __str__(self):
        return 'Turn %d' % self.turn

    def reset(self):
        self.turn = 1

    def rollback_turn(self):
        self.turn -= 1
