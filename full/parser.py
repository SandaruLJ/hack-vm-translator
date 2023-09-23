"""Parser module of the VM translator

Classes:
    Parser
"""

from constants import *

class Parser:
    """Parser class of Hack VM Translator.

    Handles the parsing of a single '.vm' file:

    Provides services for reading a VM command,
    unpacking the command into its various components,
    and providing convenient access to them.

    Properties:
        file: file object containing the source VM code
        current_command: the VM command currently being processed

    Methods:
        advance() -> bool
        command_type() -> str
        arg1() -> str
        arg2() -> int
    """

    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.current_command = ''


    def __del__(self):
        self.file.close()


    def advance(self):
        """Advance to the next command, and makes it the current command.
        Returns True if a command was found, else False.
        """
        self.current_command = ''

        while char := self.file.read(1):
            #ignore whitespace
            if char == ' ':
                if not self.current_command:
                    continue
            # ignore comments
            elif char == '/':
                if self.current_command:
                    self._format_cmd()
                    return True
                self.file.readline()
                continue
            # check for end of command
            elif char == '\n':
                if self.current_command:
                    self._format_cmd()
                    return True
                continue

            self.current_command += char

        return False


    def _format_cmd(self):
        for i in range(len(self.current_command) - 1, 0, -1):
            if self.current_command[i] != ' ':
                return
            # remove following whitespace
            self.current_command = self.current_command[0:i]


    def command_type(self):
        """Returns a the type of the current command"""

        # check for arithmetic commands
        arithmetic_cmds = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        if self.current_command in arithmetic_cmds:
            return C_ARITHMETIC

        # check for stack operation commands
        if self.current_command.startswith('push'):
            return C_PUSH
        if self.current_command.startswith('pop'):
            return C_POP

        # check for branching commands
        if self.current_command.startswith('label'):
            return C_LABEL
        if self.current_command.startswith('goto'):
            return C_GOTO
        if self.current_command.startswith('if-goto'):
            return C_IF


    def arg1(self):
        """Return the first argument of the current command.
        In the case of C_ARITHMETIC, return the command itself
        """
        if self.command_type() == C_ARITHMETIC:
            return self.current_command
        return self._get_cmd_field(2)


    def arg2(self):
        """Return the second argument of the current command"""
        return int(self._get_cmd_field(3))


    def _get_cmd_field(self, field_num):
        field_str = ''

        current_field = 0
        inside_field = False

        for char in self.current_command:
            if not inside_field and char != ' ':
                current_field += 1
                inside_field = True
            elif inside_field and char == ' ':
                inside_field = False

            if inside_field and current_field == field_num:
                field_str += char

        return field_str
