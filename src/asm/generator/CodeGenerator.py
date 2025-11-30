from asm.parser import *

class ReferenceTable:
	def __init__(self):
		pass

	def __str__(self):
		return "Tabla de referencias"

class CodeGeneratorResult:
	def __init__(self, referenceTable: ReferenceTable, code: str):
		self.referenceTable = referenceTable
		self.code = code

class CodeGenerator:
	def __init__(self):
		self.referenceTable: ReferenceTable
		pass

	def generateCode(self, instructions: list[Instruction]) -> CodeGeneratorResult:
		self.table = ReferenceTable()

		code = self._processInstructions(instructions)

		return CodeGeneratorResult(self.table, code)

	def _processInstructions(self, instructions: list[Instruction]) -> str:

		code = ""

		for instruction in instructions:
			match instruction:

				case MoveInstruction():
					pass

				case AddInstruction():
					pass

				case SubInstruction():
					pass

				case XorInstruction():
					pass

				case AndInstruction():
					pass

				case OrInstruction():
					pass

				case MovzxInstruction():
					pass

				case XchgInstruction():
					pass

				case CmpInstruction():
					pass

				case TestInstruction():
					pass

				case LeaInstruction():
					pass

				case IncInstruction():
					pass

				case DecInstruction():
					pass

				case MulInstruction():
					pass

				case ImulInstruction():
					pass

				case DivInstruction():
					pass

				case IdivInstruction():
					pass

				case PushInstruction():
					pass

				case PopInstruction():
					pass

				case IntInstruction():
					pass

				case JmpInstruction():
					pass

				case JeInstruction():
					pass

				case JneInstruction():
					pass

				case JleInstruction():
					pass

				case JlInstruction():
					pass

				case JzInstruction():
					pass

				case JnzInstruction():
					pass

				case JaInstruction():
					pass

				case JaeInstruction():
					pass

				case JbInstruction():
					pass

				case JbeInstruction():
					pass

				case JgInstruction():
					pass

				case JgeInstruction():
					pass

				case CallInstruction():
					pass

				case LoopInstruction():
					pass

				case RetInstruction():
					pass

				case NopInstruction():
					pass

				case DirectiveInstruction():
					pass

				case DataDeclarationInstruction():
					pass

				case ImulTwoInstruction():
					pass

		return code