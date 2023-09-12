"""Parser module of the VM translator

Classes:
    Parser
"""

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
    """
    
    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.current_command = ''


    def advance(self):
        """Advance to the next command, and makes it the current command"""
        self.current_command = ''

        while char := self.file.read(1):
            #ignore whitespace
            if char == ' ':
                if not self.current_command:
                    continue
            # ignore comments
            elif char == '/':
                if self.current_command:
                    return True
                self.file.readline()
                continue
            # check for end of command
            elif char == '\n':
                if self.current_command:
                    return True
                continue

            self.current_command += char

        return False
