from enum import unique, Enum


@unique
class Stone(Enum):
    WHITE = 'o'
    BLACK = 'x'
    NONE = '.'

    def __str__(self):
        return self.value
