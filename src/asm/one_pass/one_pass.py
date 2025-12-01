from typing import cast
from asm.common import *

class OnePassAssembler(AssemblerI):

	def __init__(self):
		super().__init__("1 pasada")
		self.tracker = Tracker()

	def assemble(self, filename) -> Result:

		symTable = cast(SymbolTable, None)
		refTable = cast(ReferenceTable, None)
		code = ""

		return Result(symTable, refTable, code)