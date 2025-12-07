from typing import cast
import os
from asm.common import *
from .Instruction import *

class ParseResult:
	def __init__(self, instructions: list[Instruction], symbol_table: SymbolTable):
		self.instructions = instructions
		self.symbol_table = symbol_table

class Parser:
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
					
					inst = self._parseInstruction(code)
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
	
	def _parseInstruction(self, code: str) -> Instruction:
		tokens = code.split()
		cmd = tokens[0].lower()
		ops = ' '.join(tokens[1:]) if len(tokens) > 1 else ""
		
		match cmd:
			case "mov": d, s = self._parseTwoOperands(ops); return MoveInstruction(d, s)
			case "add": d, s = self._parseTwoOperands(ops); return AddInstruction(d, s)
			case "sub": d, s = self._parseTwoOperands(ops); return SubInstruction(d, s)
			case "inc": return IncInstruction(self._parseExpression(ops))
			case "dec": return DecInstruction(self._parseExpression(ops))
			case "mul": return MulInstruction(self._parseExpression(ops))
			case "div": return DivInstruction(self._parseExpression(ops))
			case "and": d, s = self._parseTwoOperands(ops); return AndInstruction(d, s)
			case "or":  d, s = self._parseTwoOperands(ops); return OrInstruction(d, s)
			case "xor": d, s = self._parseTwoOperands(ops); return XorInstruction(d, s)
			case "test": d, s = self._parseTwoOperands(ops); return TestInstruction(d, s)
			case "cmp": d, s = self._parseTwoOperands(ops); return CmpInstruction(d, s)
			case "lea": d, s = self._parseTwoOperands(ops); return LeaInstruction(d, s)
			case "xchg": d, s = self._parseTwoOperands(ops); return XchgInstruction(d, s)
			case "movzx": d, s = self._parseTwoOperands(ops); return MovzxInstruction(d, s)
			case "push": return PushInstruction(self._parseExpression(ops))
			case "pop": return PopInstruction(self._parseExpression(ops))
			case "call": return CallInstruction(ops.strip())
			case "ret": return RetInstruction()
			case "int": return IntInstruction(self._parseExpression(ops))
			case "nop": return NopInstruction()
			case "jmp": return JmpInstruction(ops.strip())
			case "loop": return LoopInstruction(ops.strip())
			case "je": return JeInstruction(ops.strip())
			case "jne": return JneInstruction(ops.strip())
			case "jz": return JzInstruction(ops.strip())
			case "jnz": return JnzInstruction(ops.strip())
			case "jg": return JgInstruction(ops.strip())
			case "jge": return JgeInstruction(ops.strip())
			case "jl": return JlInstruction(ops.strip())
			case "jle": return JleInstruction(ops.strip())
			case "ja": return JaInstruction(ops.strip())
			case "jae": return JaeInstruction(ops.strip())
			case "jb": return JbInstruction(ops.strip())
			case "jbe": return JbeInstruction(ops.strip())
			case _: return NopInstruction()
	
	def _parseTwoOperands(self, text: str):
		comma = -1
		depth = 0
		for i, c in enumerate(text):
			if c == '[': depth += 1
			elif c == ']': depth -= 1
			elif c == ',' and depth == 0: comma = i; break
		if comma == -1: raise ValueError(f"Expected 2 operands: {text}")
		return self._parseExpression(text[:comma]), self._parseExpression(text[comma+1:])
	
	def _parseExpression(self, expr: str):
		expr = expr.strip()
		if expr.startswith('[') and expr.endswith(']'): return MemoryExpression(IdentifierExpression(expr[1:-1].strip()))
		try: 
			if expr.upper().endswith('H'): return IntegerExpression(int(expr[:-1], 16))
			if expr.upper().startswith('0X'): return IntegerExpression(int(expr, 16))
			return IntegerExpression(int(expr))
		except: return IdentifierExpression(expr)