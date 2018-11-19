from ansi_colours import AnsiColours as Colour


class Style:

    @staticmethod
    def create_underline(title):
        return Colour.light_grey("".join(['-' for _ in range(len(title))]))
