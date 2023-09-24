"""Main module of the VM translator"""

import os
import sys

from parser import Parser
from code_writer import CodeWriter
from constants import *


SOURCE_EXT = 'vm'
TARGET_EXT = 'asm'


def main():
    if len(sys.argv) != 2:
        print('Usage: program <Source>.vm || program <source_dir>')
        exit(1)

    source = sys.argv[1]
    is_dir = os.path.isdir(source)

    # determine source and target files according to user input
    if is_dir:
        # get all files with the extension '.vm' in the specified source directory
        source_files = [file.path for file in os.scandir(source)
                        if file.path.split('.')[-1] == SOURCE_EXT]
        absolute_path = os.path.abspath(source)
        target_file = f'{absolute_path}/{os.path.basename(absolute_path)}.{TARGET_EXT}'
    else:
        source_files = [source]
        target_file = parse_filename(source)[0] + f'.{TARGET_EXT}'

    # create code writer instance for the target
    writer = CodeWriter(target_file)

    for source_file in source_files:
        filename, ext = parse_filename(source_file)
        
        # check if filename and extension is valid
        if not (filename or filename[0].isupper() or ext != SOURCE_EXT):
              print(f'Invalid filename format: {filename}.{ext}')
              exit(1)

        # create parser instance for each source file
        parser = Parser(source_file)

        translate(parser, writer)

    # close target file
    writer.close()


def translate(parser, writer):
    while parser.advance():
        cmd_type = parser.command_type()

        if cmd_type == C_ARITHMETIC:
            writer.write_arithmetic(parser.current_command)
        elif cmd_type == C_PUSH or cmd_type == C_POP:
            writer.write_push_pop(cmd_type, parser.arg1(), parser.arg2())
        elif cmd_type == C_LABEL:
            writer.write_label(parser.arg1())
        elif cmd_type == C_GOTO:
            writer.write_goto(parser.arg1())
        elif cmd_type == C_IF:
            writer.write_if(parser.arg1())


def parse_filename(file):
    split_filename = file.split('.')
    
    filename = ''.join(split_filename[0:-1])
    ext = split_filename[-1]

    return filename, ext


if __name__ == '__main__':
    main()
