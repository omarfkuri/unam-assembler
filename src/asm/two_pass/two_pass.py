from .parser import Parser
from .generator import CodeGenerator

from asm.common import *

class TwoPassAssembler(AssemblerI):

	def __init__(self):
		super().__init__("2 pasadas")
		self.parser = Parser()
		self.codeGenerator = CodeGenerator()

	def assemble(self, filename) -> Result:

		print(f"Leyendo símbolos...")
		parse_result = self.parser.readInstructions(filename)

		print(f"Generando código...")
		assembler_result = self.codeGenerator.generateCode(parse_result.instructions)

		return Result(
			parse_result.symbol_table, 
			assembler_result.referenceTable, 
			assembler_result.code)