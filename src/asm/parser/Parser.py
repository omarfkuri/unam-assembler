from typing import cast
from asm.parser.Instruction import *

class SymbolTable:
	def __init__(self):
		self.symbols: dict[str, int] = {}
	
	def add_symbol(self, name: str, address: int):
		self.symbols[name] = address
	
	def get_address(self, name: str) -> int | None:
		return self.symbols.get(name)
	
	def has_symbol(self, name: str) -> bool:
		return name in self.symbols
	
	def __str__(self):
		if not self.symbols:
			return "--"
		
		lines = ["Tabla de símbolos:"]
		lines.append("-" * 40)
		lines.append(f"{'Símbolo':<20} {'Dirección':>10}")
		lines.append("-" * 40)
		
		for name, address in sorted(self.symbols.items()):
			lines.append(f"{name:<20} 0x{address:08X}")
		
		lines.append("-" * 40)
		lines.append(f"Total: {len(self.symbols)} símbolos")
		
		return "\n".join(lines)
	
	def __repr__(self):
		return f"SymbolTable({len(self.symbols)} symbols)"

class ParseResult:
	def __init__(self, instructions: list[Instruction], symbol_table: SymbolTable):
		self.instructions = instructions
		self.symbol_table = symbol_table

class Parser:
	def __init__(self):
		self.symbol_table: SymbolTable
		self.data_address = 0x0000
		self.text_address = 0x1000
		self.in_data_section = False
	
	def readInstructions(self, filename: str) -> ParseResult:
		instructions: list[Instruction] = []
		self.symbol_table = SymbolTable()
		with open(filename, "r") as file:
			for line in file.read().splitlines():
				code = line.strip()
				if code == "": continue
				
				if ';' in code:
					code = code[:code.index(';')].strip()
				if code == "": continue
				
				tokens = code.split()
				
				if tokens[0].lower() == 'section':
					self.in_data_section = '.data' in code.lower()
					continue
				
				if tokens[0].lower() == 'global':
					continue
				
				if code.endswith(':'):
					label_name = code[:-1]
					address = self.data_address if self.in_data_section else self.text_address
					self.symbol_table.add_symbol(label_name, address)
					continue
				
				if len(tokens) >= 2 and tokens[1].lower() in ['dd', 'dw', 'db']:
					label = tokens[0]
					directive = tokens[1].lower()
					value = ' '.join(tokens[2:]) if len(tokens) > 2 else ""
					
					self.symbol_table.add_symbol(label, self.data_address)
					
					size = {'db': 1, 'dw': 2, 'dd': 4}.get(directive, 4)
					self.data_address += size
					
					instructions.append(DataDeclarationInstruction(label, directive, value))
					continue
				
				inst = self._parseInstruction(code)
				instructions.append(inst)
				
				if not self.in_data_section:
					self.text_address += self._estimate_instruction_size(inst)
		
		return ParseResult(instructions, self.symbol_table)
	
	def _estimate_instruction_size(self, inst: Instruction) -> int:
		if isinstance(inst, (RetInstruction, NopInstruction)):
			return 1
		elif isinstance(inst, (JmpInstruction, JeInstruction, JneInstruction, 
		                       JleInstruction, JlInstruction, JzInstruction, 
		                       JnzInstruction, JaInstruction, JaeInstruction,
		                       JbInstruction, JbeInstruction, JgInstruction, 
		                       JgeInstruction, LoopInstruction)):
			return 2
		elif isinstance(inst, (IncInstruction, DecInstruction)):
			return 1
		elif isinstance(inst, (PushInstruction, PopInstruction)):
			return 1
		elif isinstance(inst, IntInstruction):
			return 2
		elif isinstance(inst, MoveInstruction):
			return 5
		else:
			return 3
	
	def _parseInstruction(self, code: str) -> Instruction:
		tokens = code.split()
		command = tokens[0].lower()
		
		operands_str = ' '.join(tokens[1:]) if len(tokens) > 1 else ""
		
		match command:
			case "mov":
				dest, src = self._parseTwoOperands(operands_str)
				return MoveInstruction(dest, src)
			
			case "add":
				dest, src = self._parseTwoOperands(operands_str)
				return AddInstruction(dest, src)
			
			case "sub":
				dest, src = self._parseTwoOperands(operands_str)
				return SubInstruction(dest, src)
			
			case "inc":
				op = self._parseExpression(operands_str)
				return IncInstruction(op)
			
			case "dec":
				op = self._parseExpression(operands_str)
				return DecInstruction(op)
			
			case "mul":
				op = self._parseExpression(operands_str)
				return MulInstruction(op)
			
			case "imul":
				if ',' in operands_str:
					dest, src = self._parseTwoOperands(operands_str)
					return ImulTwoInstruction(dest, src)
				else:
					op = self._parseExpression(operands_str)
					return ImulInstruction(op)
			
			case "div":
				op = self._parseExpression(operands_str)
				return DivInstruction(op)
			
			case "idiv":
				op = self._parseExpression(operands_str)
				return IdivInstruction(op)
			
			case "jmp":
				return JmpInstruction(operands_str.strip())
			
			case "cmp":
				op1, op2 = self._parseTwoOperands(operands_str)
				return CmpInstruction(op1, op2)
			
			case "je":
				return JeInstruction(operands_str.strip())
			
			case "jne":
				return JneInstruction(operands_str.strip())
			
			case "jle":
				return JleInstruction(operands_str.strip())
			
			case "jl":
				return JlInstruction(operands_str.strip())
			
			case "jz":
				return JzInstruction(operands_str.strip())
			
			case "jnz":
				return JnzInstruction(operands_str.strip())
			
			case "ja":
				return JaInstruction(operands_str.strip())
			
			case "jae":
				return JaeInstruction(operands_str.strip())
			
			case "jb":
				return JbInstruction(operands_str.strip())
			
			case "jbe":
				return JbeInstruction(operands_str.strip())
			
			case "jg":
				return JgInstruction(operands_str.strip())
			
			case "jge":
				return JgeInstruction(operands_str.strip())
			
			case "call":
				return CallInstruction(operands_str.strip())
			
			case "ret":
				return RetInstruction()
			
			case "push":
				op = self._parseExpression(operands_str)
				return PushInstruction(op)
			
			case "pop":
				op = self._parseExpression(operands_str)
				return PopInstruction(op)
			
			case "int":
				op = self._parseExpression(operands_str)
				return IntInstruction(op)
			
			case "loop":
				return LoopInstruction(operands_str.strip())
			
			case "xor":
				dest, src = self._parseTwoOperands(operands_str)
				return XorInstruction(dest, src)
			
			case "test":
				op1, op2 = self._parseTwoOperands(operands_str)
				return TestInstruction(op1, op2)
			
			case "movzx":
				dest, src = self._parseTwoOperands(operands_str)
				return MovzxInstruction(dest, src)
			
			case "xchg":
				op1, op2 = self._parseTwoOperands(operands_str)
				return XchgInstruction(op1, op2)
			
			case "and":
				dest, src = self._parseTwoOperands(operands_str)
				return AndInstruction(dest, src)
			
			case "or":
				dest, src = self._parseTwoOperands(operands_str)
				return OrInstruction(dest, src)
			
			case "lea":
				reg, mem = self._parseTwoOperands(operands_str)
				return LeaInstruction(reg, mem)
			
			case "nop":
				return NopInstruction()
			
			case _:
				raise ValueError(f"Unknown instruction: {command}")
	
	def _parseTwoOperands(self, operands_str: str) -> tuple[Expression, Expression]:
		comma_pos = self._findCommaOutsideBrackets(operands_str)
		if comma_pos == -1:
			raise ValueError(f"Expected two operands separated by comma: {operands_str}")
		
		first = operands_str[:comma_pos].strip()
		second = operands_str[comma_pos + 1:].strip()
		
		return self._parseExpression(first), self._parseExpression(second)
	
	def _findCommaOutsideBrackets(self, text: str) -> int:
		bracket_depth = 0
		for i, char in enumerate(text):
			if char == '[':
				bracket_depth += 1
			elif char == ']':
				bracket_depth -= 1
			elif char == ',' and bracket_depth == 0:
				return i
		return -1
	
	def _parseExpression(self, expr: str) -> Expression:
		expr = expr.strip()
		
		if expr.startswith('[') and expr.endswith(']'):
			inner = expr[1:-1].strip()
			address_expr = self._parseAddressExpression(inner)
			return MemoryExpression(address_expr)
		
		if self._isInteger(expr):
			return IntegerExpression(self._parseInteger(expr))
		
		return IdentifierExpression(expr)
	
	def _parseAddressExpression(self, expr: str) -> Expression:
		expr = expr.strip()
		
		operator_pos = -1
		operator = None
		bracket_depth = 0
		
		for i in range(len(expr) - 1, -1, -1):
			char = expr[i]
			if char == ']':
				bracket_depth += 1
			elif char == '[':
				bracket_depth -= 1
			elif bracket_depth == 0 and char in ['+', '-']:
				operator_pos = i
				operator = char
				break
		
		if operator_pos != -1:
			left = expr[:operator_pos].strip()
			right = expr[operator_pos + 1:].strip()
			return BinaryExpression(
				self._parseAddressExpression(left),
				cast(str, operator),
				self._parseAddressExpression(right)
			)
		
		if self._isInteger(expr):
			return IntegerExpression(self._parseInteger(expr))
		
		return IdentifierExpression(expr)
	
	def _isInteger(self, s: str) -> bool:
		s = s.strip().upper()
		
		if s.endswith('H'):
			try:
				int(s[:-1], 16)
				return True
			except ValueError:
				return False

		if s.startswith('0X'):
			try:
				int(s, 16)
				return True
			except ValueError:
				return False
		
		try:
			int(s, 10)
			return True
		except ValueError:
			return False
	
	def _parseInteger(self, s: str) -> int:
		s = s.strip().upper()
		
		if s.endswith('H'):
			return int(s[:-1], 16)
		
		if s.startswith('0X'):
			return int(s, 16)
		
		return int(s, 10)