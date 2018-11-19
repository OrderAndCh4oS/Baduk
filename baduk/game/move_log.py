class MoveLog:

    def __init__(self):
        self.moves = []
        self.count = 0

    def add(self, move):
        self.moves.append(move)
        self.count += 1

    def pop(self):
        self.count -= 1
        return self.moves.pop()

    def count(self):
        return self.count

    def reset(self):
        self.moves = []
        self.count = 0
