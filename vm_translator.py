"""Main module of the VM translator"""

import sys

from parser import Parser
from constants import *


def main():
    if len(sys.argv) != 2:
        print('Usage: program <source>.vm')
        exit(1)

    parser = Parser(sys.argv[1])
    
    while parser.advance():
        cmd_type = parser.command_type()

        if cmd_type == C_ARITHMETIC:
            pass
        elif cmd_type == C_PUSH or cmd_type == C_POP:
            pass


if __name__ == '__main__':
    main()
