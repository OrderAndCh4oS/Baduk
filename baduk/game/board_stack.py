class BoardStack:

    def __init__(self):
        self.past_board_states = []

    def push(self, board):
        self.past_board_states.append(str(board))
        if len(self.past_board_states) > 2:
            del self.past_board_states[0]

    def breaks_simple_ko_rule(self, current_board):
        if len(self.past_board_states) < 2:
            return False
        return str(current_board) == self.past_board_states[-2]

    def reset(self):
        self.past_board_states = []

    def remove_last(self):
        if len(self.past_board_states):
            del self.past_board_states[-1]
