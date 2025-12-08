from asm.common import *
from asm.common.inst import *

class ParseResult:
	def __init__(self, instructions: list[Instruction], symbol_table: SymbolTable):
		self.instructions = instructions
		self.symbol_table = symbol_table

class Parser(InstructionParser):
	def __init__(self):
		self.symbol_table: SymbolTable
	
	def readInstructions(self, filename: str) -> ParseResult:
		self.symbol_table = SymbolTable()
		self.current_address = 0x1000 
		instructions: list[Instruction] = []

		try:
			with open(filename, "r", encoding="utf-8") as file:
				lines = file.read().splitlines()
				for line in lines:
					code = line.strip()
					if not code or code.startswith(';'): continue
					if ';' in code: code = code[:code.index(';')].strip()
					if not code: continue
					
					tokens = code.split()
					if tokens[0].lower() in ['section', 'global']: continue
					
					if code.endswith(':'):
						self.symbol_table.add_symbol(code[:-1], self.current_address)
						continue
					
					if len(tokens) >= 2 and tokens[1].lower() in ['dd', 'dw', 'db']:
						label, directive = tokens[0], tokens[1].lower()
						value = ' '.join(tokens[2:]) if len(tokens) > 2 else ""
						self.symbol_table.add_symbol(label, self.current_address)
						self.current_address += {'db': 1, 'dw': 2, 'dd': 4}.get(directive, 4)
						instructions.append(DataDeclarationInstruction(label, directive, value))
						continue
					
					inst = self.parseInstruction(code)
					instructions.append(inst)
					self.current_address += self._estimateInstSize(inst)
		
		except Exception as e:
			print(f"Error parseando: {e}")
		return ParseResult(instructions, self.symbol_table)
	
	def _estimateInstSize(self, inst: Instruction) -> int:
		match inst:
			# 1 Byte
			case RetInstruction() | NopInstruction() | PushInstruction() | PopInstruction() | IncInstruction() | DecInstruction(): return 1
			# 2 Bytes (Saltos cortos, Reg-Reg, Int)
			case (JmpInstruction() | LoopInstruction() | IntInstruction() |
				  JeInstruction() | JneInstruction() | JleInstruction() | JlInstruction() | 
				  JzInstruction() | JnzInstruction() | JaInstruction() | JaeInstruction() |
				  JbInstruction() | JbeInstruction() | JgInstruction() | JgeInstruction()): return 2
			# Call (E8 + 32-bit offset) = 5 bytes
			case CallInstruction(): return 5
			
			# Lógica y Movimientos
			case MoveInstruction():
				if isinstance(inst.src, IntegerExpression): return 5 # B8 + imm32
				if isinstance(inst.dest, MemoryExpression) or isinstance(inst.src, MemoryExpression): return 6
				return 2
			case CmpInstruction() | TestInstruction() | LeaInstruction():
				if hasattr(inst, 'op2') and isinstance(inst.op2, MemoryExpression): return 6
				if hasattr(inst, 'mem'): return 6 # LEA
				if hasattr(inst, 'op2') and isinstance(inst.op2, IntegerExpression): return 3
				return 2
			case AndInstruction() | OrInstruction() | XorInstruction() | AddInstruction() | SubInstruction() | MovzxInstruction() | XchgInstruction():
				return 2
			case MulInstruction() | DivInstruction(): return 2
			case _: return 1
	