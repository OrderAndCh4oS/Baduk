from baduk.command.command_types import Command, UndoableCommand


class ChainOfCommands:
    stack = []

    def execute_command(self, command: Command):
        result = command.execute()
        if isinstance(command, UndoableCommand):
            self.stack.append(command)
        return result

    def undo(self):
        if len(self.stack):
            command = self.stack.pop()
            command.undo()

    def reset(self):
        self.stack = []
