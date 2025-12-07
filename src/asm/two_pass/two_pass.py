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
		# Pasada 1: El parser lee el archivo y genera la tabla de símbolos
		parse_result = self.parser.readInstructions(filename)

		print(f"Generando código...")
		# Pasada 2: El generador usa las instrucciones y la tabla para crear el hex
		assembler_result = self.codeGenerator.generateCode(
			parse_result.instructions, 
			parse_result.symbol_table
		)

		return Result(
			parse_result.symbol_table, 
			assembler_result.referenceTable, 
			assembler_result.code)