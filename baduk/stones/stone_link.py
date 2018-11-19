from baduk.enums.enums import Stone


class StoneLink:
    group = None

    def __init__(self, point, stone):
        self.point = point
        self.stone = stone

    # def __repr__(self):
    #     return '%s: %s' % (str(self.point), str(self.stone))

    def set_group(self, group):
        self.group = group

    def set_stone(self, stone):
        self.stone = stone

    def get_adjacent_stones(self, board):
        return self.point.filter_adjacent_links(
            lambda adjacent_link: self.stone == adjacent_link.stone,
            board
        )

    def get_adjacent_groups(self, board):
        return self.point.filter_adjacent_links(
            lambda adjacent_link: adjacent_link.stone != Stone.NONE,
            board
        )

    def find_adjacent(self, links, liberties, board):
        for adjacent_point in self.point.adjacent_points():
            if board.in_grid(adjacent_point):
                adjacent_link = board.get_point_stone_link(**adjacent_point)
                self.set_links_and_liberties(adjacent_link, board, liberties, links)

    def set_links_and_liberties(self, adjacent_link, board, liberties, links):
        if adjacent_link.stone == Stone.NONE:
            liberties.add(adjacent_link)
        elif adjacent_link.stone == self.stone and adjacent_link not in links:
            links.add(adjacent_link)
            adjacent_link.find_adjacent(links, liberties, board)
