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
        instructions = self._generate_arithmetic_instructions(command, self.unique_num)
        self._write_instructions(instructions)


    def write_push_pop(self, command, segment, index):
        """Write to the output file,
        the assembly code that implements the given push or pop command.
        """
        # generate common stack operation snippets
        seg_to_d, d_to_stack, stack_to_d, d_to_seg = \
            self._generate_push_pop_snippets(segment, index)

        # determine memory segment mapping
        if segment == 'local':
            mem_seg = 'LCL'
        elif segment == 'argument':
            mem_seg = 'ARG'
        else:  # this, that, and temp
            mem_seg = segment.upper()

        if command == C_PUSH:
            self._write_comment(f'push {segment} {index}')

            if segment == 'constant':
                instructions = [
                    f'@{index}',
                    'D=A',
                    '\n'.join(d_to_stack)
                ]

            # special case for static segment
            elif segment == 'static':
                filename = ''.join(self.file.name.split('.')[0:-1])
                instructions = [
                    f'@{filename}.{index}',
                    'D=M',
                    '\n'.join(d_to_stack)
                ]

            # special case for pointer segment
            elif segment == 'pointer':
                instructions = [
                    '@THIS' if index == 0 else '@THAT',
                    'D=M',
                    '\n'.join(d_to_stack)
                ]

            # local, argument, this, that, and temp
            else:
                instructions = [
                    '\n'.join(seg_to_d).format(seg=mem_seg),
                    '\n'.join(d_to_stack)
                ]

            self._write_instructions(instructions)

        # pop commands
        else:
            self._write_comment(f'pop {segment} {index}')

            # special case for static segment
            if segment == 'static':
                filename = ''.join(self.file.name.split('.')[0:-1])
                instructions = [
                    '\n'.join(stack_to_d),
                    f'@{filename}.{index}',
                    'M=D'
                ]

            # special case for pointer segment
            elif segment == 'pointer':
                instructions = [
                    '\n'.join(stack_to_d),
                    '@THIS' if index == 0 else '@THAT',
                    'M=D'
                ]

            # local, argument, this, that, and temp
            else:
                instructions = [
                    '\n'.join(stack_to_d),
                    '\n'.join(d_to_seg).format(seg=mem_seg)
                ]

            self._write_instructions(instructions)


    @staticmethod
    def _generate_arithmetic_instructions(command, unique_num):
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
                    op=command.upper(), unique=unique_num)
                )

            # set final stack value
            instruction.append('M=D')

        return instruction


    @staticmethod
    def _generate_push_pop_snippets(segment, index):
        # move memory segment register to D
        seg_to_d = [
            f'@{index}',
            'D=A',
            '@' + ('5' if segment == 'temp' else '{seg}'),
            'A=D+' + ('A' if segment == 'temp' else 'M'),
            'D=M'
        ]
        # move from D to stack
        d_to_stack = [
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D'
        ]
        # move from stack to a temporary memory register
        stack_to_d = [
            '@SP',
            'M=M-1',
            'A=M',
            'D=M'
        ]
        # move from temporary memory register to memory segment register
        d_to_seg = [
            '@R13',  # store value here temporarily
            'M=D',
            f'@{index}',
            'D=A',
            '@' + ('5' if segment == 'temp' else '{seg}'),
            'D=D+' + ('A' if segment == 'temp' else 'M'),
            '@R14',  # store memory segment pointer here
            'M=D',
            '@R13',  # where value from stack was stored in
            'D=M',
            '@R14',
            'A=M',   # load memory segment pointer back to A
            'M=D'
        ]

        return seg_to_d, d_to_stack, stack_to_d, d_to_seg


    def _write_instructions(self, instructions):
        self.file.write('\n'.join(instructions) + '\n')
        self.unique_num += 1


    def close(self):
        """Close the output file"""
        self.file.close()
