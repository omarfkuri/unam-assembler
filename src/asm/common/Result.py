from .ReferenceTable import *
from .SymbolTable import *

class Result:
	def __init__(self, 
			symbolTable: SymbolTable, 
			referenceTable: ReferenceTable, 
			machineCode: str):

		self.symbolTable = symbolTable
		self.referenceTable = referenceTable
		self.machineCode = machineCode