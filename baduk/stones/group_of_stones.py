from baduk.enums.enums import Stone
from baduk.stones.stone_link import StoneLink


class GroupOfStones:
    def __init__(self, link: StoneLink):
        self.stone = link.stone
        self.links = set()
        self.liberties = set()
        link.set_group(self)
        self.first_link = link
        self.links.add(link)

    #
    # def __repr__(self):
    #     return 'Key: %s | Liberties %d' % (
    #         (', '.join([str(link) for link in self.links])), len(self.liberties))

    def update(self, board):
        self.links.clear()
        self.links.add(self.first_link)
        self.liberties.clear()
        self.first_link.find_adjacent(self.links, self.liberties, board)

    def add_link(self, link: StoneLink):
        link.set_group(self)
        self.links.add(link)

    def get_liberties(self):
        return len(self.liberties)

    def get_links(self):
        return self.links

    def merge(self, group):
        self.links = group.links | self.links
        self.liberties = group.liberties | self.liberties

    def set_links_group(self):
        for link in self.links:
            link.set_group(self)

    def count_stones(self):
        return len(self.links)

    def remove_stone_from_board(self, stone_link):
        stone_link.set_stone(Stone.NONE)
        stone_link.set_group(None)
        self.links.remove(stone_link)

    def capture_stones(self):
        for link in self.links:
            link.set_stone(Stone.NONE)
            link.set_group(None)

    def replace_captured_stones(self):
        for link in self.links:
            link.set_stone(self.stone)
            link.set_group(self)
