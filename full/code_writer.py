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
        set_filename(str) -> None
        write_arithmetic(str) -> None
        write_push_pop(str, str, int) -> None
        write_label(str) -> None
        write_goto(str) -> None
        write_if(str) -> None
        write_function(str, int) -> None
        write_return() -> None
        write_call() -> None
    """

    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.unique_num = 0  # for making each symbolic label globally unique
        self.source = ''
        self.function_calls = {}  # ex: {"function_name": num_calls}

        self._write_bootstrap_code()


    def _write_bootstrap_code(self):
        instructions = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        # set stack pointer to 256
        self._write_instructions(instructions)
        # call Sys.init
        self.write_call('Sys.init', 0)


    def set_filename(self, filename):
        """Inform that the translation of a new VM file has started.
        Set the name of the current source file being translated.
        """
        self.source = filename.split('/')[-1]


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
                instructions = [
                    f'@{self.source}.{index}',
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
                instructions = [
                    '\n'.join(stack_to_d),
                    f'@{self.source}.{index}',
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


    def write_label(self, label):
        """Write to the output file,
        the assembly code that implements the label command.
        """
        self._write_comment(f'label {label}')
        instructions = [f'({label})']
        self._write_instructions(instructions)


    def write_goto(self, label):
        """Write to the output file,
        the assembly code that implements the unconditional goto command.
        """
        self._write_comment(f'goto {label}')
        instructions = [
            f'@{label}',
            '0;JMP',
        ]
        self._write_instructions(instructions)


    def write_if(self, label):
        """Write to the output file,
        the assembly code that implements the conditional goto command.
        """
        self._write_comment(f'if-goto {label}')
        instructions = [
            '@SP',
            'AM=M-1',
            'D=M',
            f'@{label}',
            'D;JNE'
        ]
        self._write_instructions(instructions)


    def write_function(self, function, local_variables):
        """Write to the output file,
        the assembly code that implements the function command.
        """
        self._write_comment(f'function {function} {local_variables}')

        # create function entry label
        instructions = [f'({function})']

        # assign local memory segment
        instructions += [
            '@SP',
            'D=M',
            '@LCL',
            'M=D'
        ]

        # initialize local variables
        for _ in range(local_variables):
            instructions += [
                '@0',
                'D=A',
                '@SP',
                'M=M+1',
                'A=M-1',
                'M=D'
            ]

        self._write_instructions(instructions)


    def write_call(self, function, num_arguments):
        """Write assembly code that effects the call command."""
        self._write_comment(f'call {function} {num_arguments}')

        try:
            self.function_calls[function] += 1
            call_num = self.function_calls[function]
        except (KeyError):
            self.function_calls[function] = 0
            call_num = 0

        return_address = f'{function}$ret.{call_num}'

        instructions = [
            f'@{return_address}',
            'D=A',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',                      # push return address label to stack
            self._push_segment('LCL'),
            self._push_segment('ARG'),
            self._push_segment('THIS'),
            self._push_segment('THAT'),
            f'@{5 + num_arguments}',    # number to subtract from SP to get to ARG
            'D=A',
            '@SP',
            'D=M-D',
            '@ARG',
            'M=D',                      # reposition ARG
            '@SP',
            'D=M',
            '@LCL',
            'M=D',                      # reposition LCL
            f'@{function}',
            '0;JMP',                    # call function (transfer control to callee)
            f'({return_address})'       # inject return address label into the code
        ]

        self._write_instructions(instructions)


    @staticmethod
    def _push_segment(segment):
        instructions = [
            f'@{segment}',
            'D=M',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D'
        ]
        return '\n'.join(instructions)


    def write_return(self):
        """Write to the output file,
        the assembly code that implements the return command.
        """
        self._write_comment('return')

        instructions = [
            '@LCL',
            'D=M',
            '@R13',
            'M=D',      # save LCL (end of frame) in temporary variable
            '@5',
            'A=D-A',
            'D=M',
            '@R14',
            'M=D',      # save return address in temporary variable
            '@SP',
            'A=M-1',
            'D=M',
            '@ARG',
            'A=M',
            'M=D',      # reposition return value for the caller
            'D=A+1',
            '@SP',
            'M=D',      # reposition stack pointer for the caller
            '@R13',
            'AM=M-1',
            'D=M',
            '@THAT',
            'M=D',      # restore THAT (that segment) for the caller
            '@R13',
            'AM=M-1',
            'D=M',
            '@THIS',
            'M=D',      # restore THIS (this segment) for the caller
            '@R13',
            'AM=M-1',
            'D=M',
            '@ARG',
            'M=D',      # restore ARG (argument segment) for the caller
            '@R13',
            'AM=M-1',
            'D=M',
            '@LCL',
            'M=D',      # restore LCL (local segment) for the caller
            '@R14',
            'A=M',
            '0;JMP'     # go to the return address
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


    def _write_comment(self, comment):
        self.file.write(f'// {comment}\n')


    def _write_instructions(self, instructions):
        self.file.write('\n'.join(instructions) + '\n')
        self.unique_num += 1


    def close(self):
        """Close the output file"""
        self.file.close()
