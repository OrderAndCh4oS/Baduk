from abc import ABCMeta, abstractmethod


class Action(metaclass=ABCMeta):

    def __call__(self, input_value):
        self.execute(input_value)

    @abstractmethod
    def execute(self, input_value):
        pass
