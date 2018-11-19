from ansi_colours import AnsiColours as Colour

from baduk.ui.style import Style
from baduk.ui.table import Table
from baduk.ui.user_input import UserInput
from baduk.ui.view import View


class Pagination:

    def __init__(self, arr, headers):
        self.arr = arr
        self.headers = headers

    def __call__(self, limit=5, find=None, find_by_id=None):
        self.limit = limit
        self.total = len(self.arr)
        self.page = 1
        return self.menu()

    def menu(self):
        result = False
        while not result:
            self.paginated_table()
            self.pagination_text()
            user_input = UserInput.get_input('\nEnter a %s, use %s and %s to navigate, or %s to go back: ' % (
                Colour.green("'number'"),
                Colour.green("<"),
                Colour.green(">"),
                Colour.green("b")
            ))
            if user_input == 'b':
                break
            if self.should_change_page(user_input):
                self.change_page(user_input)
                continue
            if user_input not in [str(x) for x in range(1, len(self.arr) + 1)]:
                continue
            result = self.arr[int(user_input) - 1]
            View().render(text="An item with that key was not found. Press any key to continue.")
        return result

    def paginated_table(self):
        arr_start = (self.page * self.limit) - self.limit
        arr_end = (self.page * self.limit)
        Table.create_table(
            self.arr[arr_start:arr_end],
            self.headers
        )

    def pagination_text(self):
        text = ""
        if self.page > 1:
            text += "%s previous | " % Colour.green('<')
        text += "page %d" % self.page
        if self.page * self.limit < self.total:
            text += " | next %s" % Colour.green('>')
        output = Style.create_underline(text)
        output += text
        output += Style.create_underline(text)

    def should_change_page(self, user_input):
        return user_input is '<' or user_input is '>'

    def change_page(self, user_input):
        if self.page is not 1 and user_input is '<':
            self.page -= 1
        elif self.page * self.limit < self.total and user_input is '>':
            self.page += 1
