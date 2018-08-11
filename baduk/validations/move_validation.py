from baduk.exceptions import ValidationError
from baduk.stones.enums import Stone


class MoveValidation:
    @staticmethod
    def check_stone_link_is_empty(stone_link):
        if stone_link.stone != Stone.NONE:
            raise ValidationError('Stone cannot be placed on another stone')

    @staticmethod
    def check_point_is_in_bounds(point, size):
        if point.x < 0 or point.x > size[0] - 1 or point.y > size[1] - 1 or point.y < 0:
            raise ValidationError('Stone placed out of bounds')
