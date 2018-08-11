from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):

    @abstractmethod
    def execute(self):
        pass


class UndoableCommand(Command, metaclass=ABCMeta):

    @abstractmethod
    def undo(self):
        pass
