from asm.common import *
from .Instruction import *

class InstructionParser:
	
	def parseInstruction(self, code: str) -> Instruction:
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