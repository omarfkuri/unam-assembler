from asm.parser import Parser, SymbolTable
from asm.generator import CodeGenerator, ReferenceTable

class Result:
	def __init__(self, 
			symbolTable: SymbolTable, 
			referenceTable: ReferenceTable, 
			machineCode: str):

		self.symbolTable = symbolTable
		self.referenceTable = referenceTable
		self.machineCode = machineCode

class Asm:

	def __init__(self):
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