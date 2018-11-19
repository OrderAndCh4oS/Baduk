from text_template import TextTemplate

from baduk.constants.resource_path import TEMPLATE_PATH


class View:

    def __init__(self, template="blank.txt"):
        self.template_path = TEMPLATE_PATH + template

    def render(self, **kwargs):
        print(TextTemplate.render(self.template_path, **kwargs))
