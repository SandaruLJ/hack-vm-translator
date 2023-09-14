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


	def _write_comment(self, comment):
		self.file.write(f'// {comment}\n')


	def write_arithmetic(self, command):
		"""Write to the output file,
		the assembly code that implements the given arithmetic-logic command.
		"""
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


	def _write_instructions(self, instructions):
		self.file.write('\n'.join(instructions) + '\n')


	def close(self):
		self.file.close()
