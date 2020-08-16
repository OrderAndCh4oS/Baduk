from ansi_colours import AnsiColours as Colour
from terminal_table.table import Table

from baduk.ui.style import Style
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
            View().render(text=self.paginated_table())
            View().render(text=self.pagination_text())
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
        return Table.create(
            self.arr[arr_start:arr_end],
            self.headers
        )

    def pagination_text(self):
        text = ""
        if self.page > 1:
            text += "< previous | "
        text += "page %d" % self.page
        if self.page * self.limit < self.total:
            text += " | next >"
        output = Style.create_underline(text)
        output += "\n%s\n" % text
        output += Style.create_underline(text)

        return output

    def should_change_page(self, user_input):
        return user_input == '<' or user_input == '>'

    def change_page(self, user_input):
        if self.page != 1 and user_input == '<':
            self.page -= 1
        elif self.page * self.limit < self.total and user_input == '>':
            self.page += 1
