"""Main module of the VM translator"""

import sys

from parser import Parser
from code_writer import CodeWriter
from constants import *


def main():
    if len(sys.argv) != 2:
        print('Usage: program <source>.vm')
        exit(1)

    filename, ext = parse_filename(sys.argv[1])
    
    # check if filename and extension is valid
    if not (filename or filename[0].isupper() or ext != 'vm'):
          print('Invalid filename format')
          exit(1)

    parser = Parser(sys.argv[1])
    writer = CodeWriter(f'{filename}.asm')

    while parser.advance():
        cmd_type = parser.command_type()

        if cmd_type == C_ARITHMETIC:
            writer.write_arithmetic(parser.current_command)
        elif cmd_type == C_PUSH or cmd_type == C_POP:
            writer.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

    writer.close()


def parse_filename(file):
    split_filename = file.split('.')
    
    filename = ''.join(split_filename[0:-1])
    ext = split_filename[-1]

    return filename, ext


if __name__ == '__main__':
    main()
