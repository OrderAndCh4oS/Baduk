from baduk.enums.enums import Stone
from baduk.exception.exceptions import ValidationError


class MoveValidation:
    @staticmethod
    def check_stone_link_is_empty(stone_link):
        if stone_link.stone != Stone.NONE:
            raise ValidationError('Stone cannot be placed on another stone')

    @staticmethod
    def check_point_is_in_bounds(point, size):
        if point.x < 0 or point.x > size[0] - 1 or point.y > size[1] - 1 or point.y < 0:
            raise ValidationError('Stone placed out of bounds')

    @staticmethod
    def check_self_capture(group, has_dead_stones, chain_of_commands):
        if not has_dead_stones and group.get_liberties() == 0:
            chain_of_commands.undo()
            raise ValidationError("Self capture is illegal")

    @staticmethod
    def breaks_simple_ko_rule(group_of_stones_collection, dead_stones, board):
        if group_of_stones_collection.dead_stone_count == 1 and board.board_stack.breaks_simple_ko_rule(board):
            group_of_stones_collection.chain_of_commands.undo()
            group_of_stones_collection.chain_of_commands.undo()
            group_of_stones_collection.update_groups_of_stones(board, dead_stones)
            raise ValidationError('Breaks simple Ko Rule')
