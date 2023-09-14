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
	"""

	def __init__(self, filename):
		self.file = open(filename, 'w')


	def _write_comment(self, comment):
		self.file.write(f'// {comment}\n')


	def write_arithmetic(self, command):
		if command == 'add':
			self._write_comment(command)
			instructions = [
				'@SP',
				'M=M-1',
				'A=M',
				'D=M',
				'A=A-1',
				'D=D+M',
				'M=D'
			]
			self.file.write('\n'.join(instructions))


	def close(self):
		self.file.close()
