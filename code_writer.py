"""Code writer module of the VM translator

Classes:
    CodeWriter
"""

from constants import *

class CodeWriter:
    """CodeWriter class of the Hack VM Translator.

    Translates a parsed VM command into Hack assembly code.

    Properties:
        file: file object of the output file

    Methods:
        write_arithmetic(str) -> None
        write_push_pop(str, str, int) -> None
    """

    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.unique_num = 0  # for making each symbolic label globally unique


    def _write_comment(self, comment):
        self.file.write(f'// {comment}\n')


    def write_arithmetic(self, command):
        """Write to the output file,
        the assembly code that implements the given arithmetic-logic command.
        """
        self._write_comment(command)
        instructions = self._generate_arithmetic_instructions(command)
        self._write_instructions(instructions)



    def write_push_pop(self, command, segment, index):
        """Write to the output file,
        the assembly code that implements the given push or pop command.
        """
        if command == C_PUSH:
            self._write_comment(f'push {segment} {index}')

            if segment == 'constant':
                instructions = [
                    f'@{index}',
                    'D=A',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
                self._write_instructions(instructions)


    def _generate_arithmetic_instructions(self, command):
        # common instruction snippets
        single_operand_prep = [
            '@SP',
            'A=M',
            'A=A-1'
        ]
        double_operand_prep = [
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            'A=A-1',
        ]
        equality_operation = [
            'D=M-D',
            '@{op}_{unique}',
            'D;J{op}',
            'D=0',
            '@FINALIZE_{unique}',
            '0;JMP',
            '({op}_{unique})',
            'D=-1',
            '(FINALIZE_{unique})',
            '@SP',
            'A=M-1'
        ]

        instruction = []

        # single operand operations
        if command == 'neg' or command == 'not':
            instruction.append('\n'.join(single_operand_prep))

            if command == 'neg':
                instruction.append('M=-M')
            else:
                instruction.append('M=!M')

        # double operand operations
        else:
            instruction.append('\n'.join(double_operand_prep))

            if command == 'add':
                instruction.append('D=M+D')
            elif command == 'sub':
                instruction.append('D=M-D')
            elif command == 'and':
                instruction.append('D=M&D')
            elif command == 'or':
                instruction.append('D=M|D')

            # equality operations
            else:
                # format equality operation snippet
                instruction.append('\n'.join(equality_operation).format(
                    op=command.upper(), unique=self.unique_num)
                )

            # set final stack value
            instruction.append('M=D')

        return instruction


    def _write_instructions(self, instructions):
        self.file.write('\n'.join(instructions) + '\n')
        self.unique_num += 1


    def close(self):
        """Close the output file"""
        self.file.close()
