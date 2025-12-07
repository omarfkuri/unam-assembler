#Procesa las instrucciones

class InstructionProcessor:

	def __init__(self, ensamblador):
		self.ensamblador = ensamblador
		self.registros = {
			'eax': 0, 'ecx': 1, 'edx': 2, 'ebx': 3,
			'esp': 4, 'ebp': 5, 'esi': 6, 'edi': 7,
			'ax': 0, 'cx': 1, 'dx': 2, 'bx': 3,
			'sp': 4, 'bp': 5, 'si': 6, 'di': 7,
			'al': 0, 'cl': 1, 'dl': 2, 'bl': 3,
			'ah': 4, 'ch': 5, 'dh': 6, 'bh': 7,
		}

#dependiendo la instrucción, llama a la función correspondiente
	def procesar(self, mnemonica: str, operandos: str):
		match mnemonica.lower():
			case 'mov':
				self.procesar_mov(operandos)
			case 'add':
				self.procesar_add(operandos)
			case 'sub':
				self.procesar_sub(operandos)
			case 'xor':
				self.procesar_xor(operandos)
			case 'and':
				self.procesar_and(operandos)
			case 'or':
				self.procesar_or(operandos)
			case 'movzx':
				self.procesar_movzx(operandos)
			case 'xchg':
				self.procesar_xchg(operandos)
			case 'cmp':
				self.procesar_cmp(operandos)
			case 'test':
				self.procesar_test(operandos)
			case 'lea':
				self.procesar_lea(operandos)
			case 'inc':
				self.procesar_inc(operandos)
			case 'dec':
				self.procesar_dec(operandos)
			case 'mul':
				self.procesar_mul(operandos)
			case 'imul':
				self.procesar_imul(operandos)
			case 'div':
				self.procesar_div(operandos)
			case 'idiv':
				self.procesar_idiv(operandos)
			case 'push':
				self.procesar_push(operandos)
			case 'pop':
				self.procesar_pop(operandos)
			case 'int':
				self.procesar_int(operandos)
			case 'jmp':
				self.procesar_jmp(operandos)
			case 'je':
				self.procesar_je(operandos)
			case 'jne':
				self.procesar_jne(operandos)
			case 'jle':
				self.procesar_jle(operandos)
			case 'jl':
				self.procesar_jl(operandos)
			case 'jz':
				self.procesar_jz(operandos)
			case 'jnz':
				self.procesar_jnz(operandos)
			case 'ja':
				self.procesar_ja(operandos)
			case 'jae':
				self.procesar_jae(operandos)
			case 'jb':
				self.procesar_jb(operandos)
			case 'jbe':
				self.procesar_jbe(operandos)
			case 'jg':
				self.procesar_jg(operandos)
			case 'jge':
				self.procesar_jge(operandos)
			case 'call':
				self.procesar_call(operandos)
			case 'loop':
				self.procesar_loop(operandos)
			case 'ret':
				self.procesar_ret()
			case 'nop':
				self.procesar_nop()
			case _:
				print(f"  Advertencia: Instrucción '{mnemonica}' no soportada")

#MOV: mov r/m32, imm32 o mov r/m32, r32
	def procesar_mov(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  MOV {dest}, {src}")

		#mov eax, imm32 (B8 + imm32)
		if dest.lower() == 'eax' and (src.startswith('0x') or src.isdigit()):
			self.ensamblador._agregar_bytes([0xB8])
			valor = int(src, 16) if src.startswith('0x') else int(src)
			self.ensamblador._agregar_dword(valor)

		#mov ecx, imm32
		elif dest.lower() == 'ecx' and (src.startswith('0x') or src.isdigit()):
			self.ensamblador._agregar_bytes([0xB9])
			valor = int(src, 16) if src.startswith('0x') else int(src)
			self.ensamblador._agregar_dword(valor)

		#mov edx, imm32
		elif dest.lower() == 'edx' and (src.startswith('0x') or src.isdigit()):
			self.ensamblador._agregar_bytes([0xBA])
			valor = int(src, 16) if src.startswith('0x') else int(src)
			self.ensamblador._agregar_dword(valor)

		#mov ebx, imm32
		elif dest.lower() == 'ebx' and (src.startswith('0x') or src.isdigit()):
			self.ensamblador._agregar_bytes([0xBB])
			valor = int(src, 16) if src.startswith('0x') else int(src)
			self.ensamblador._agregar_dword(valor)

		#mov ecx, [dirección] (8B 0D [addr])
		elif dest.lower() == 'ecx' and src.startswith('['):
			self.ensamblador._agregar_bytes([0x8B, 0x0D])
			self.ensamblador._agregar_dword(0)

		#mov eax, [dirección] (A1 [addr]) - forma corta
		elif dest.lower() == 'eax' and src.startswith('['):
			self.ensamblador._agregar_bytes([0xA1])
			self.ensamblador._agregar_dword(0)

		#mov ebx, [dirección] (8B 1D [addr])
		elif dest.lower() == 'ebx' and src.startswith('['):
			self.ensamblador._agregar_bytes([0x8B, 0x1D])
			self.ensamblador._agregar_dword(0)

		#mov edx, [dirección] (8B 15 [addr])
		elif dest.lower() == 'edx' and src.startswith('['):
			self.ensamblador._agregar_bytes([0x8B, 0x15])
			self.ensamblador._agregar_dword(0)

		#mov [dirección], eax (A3 [addr]) - forma corta
		elif src.lower() == 'eax' and dest.startswith('['):
			self.ensamblador._agregar_bytes([0xA3])
			self.ensamblador._agregar_dword(0)

		#mov [dirección], ecx (89 0D [addr])
		elif src.lower() == 'ecx' and dest.startswith('['):
			self.ensamblador._agregar_bytes([0x89, 0x0D])
			self.ensamblador._agregar_dword(0)

		#mov [dirección], ebx (89 1D [addr])
		elif src.lower() == 'ebx' and dest.startswith('['):
			self.ensamblador._agregar_bytes([0x89, 0x1D])
			self.ensamblador._agregar_dword(0)

		#mov registro, registro (89 /r)
		elif dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x89, 0xC0 + (src_reg << 3) + dest_reg])

#add para add r32, r32
	def procesar_add(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  ADD {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x01, 0xC0 + (src_reg << 3) + dest_reg])

#sub para sub r32, r32
	def procesar_sub(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  SUB {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x29, 0xC0 + (src_reg << 3) + dest_reg])

#xor para xor r32, r32
	def procesar_xor(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  XOR {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x31, 0xC0 + (src_reg << 3) + dest_reg])

#and para and r32, r32
	def procesar_and(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  AND {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x21, 0xC0 + (src_reg << 3) + dest_reg])

# or r32, r32
	def procesar_or(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  OR {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x09, 0xC0 + (src_reg << 3) + dest_reg])

#movzx r32, r/m8
	def procesar_movzx(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  MOVZX {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x0F, 0xB6, 0xC0 + (dest_reg << 3) + src_reg])

#xchg r32, r32
	def procesar_xchg(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  XCHG {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			if dest.lower() == 'eax':
				self.ensamblador._agregar_bytes([0x90 + src_reg])
			elif src.lower() == 'eax':
				self.ensamblador._agregar_bytes([0x90 + dest_reg])
			else:
				self.ensamblador._agregar_bytes([0x87, 0xC0 + (dest_reg << 3) + src_reg])

#cmp r32, imm8
	def procesar_cmp(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  CMP {dest}, {src}")

		if dest.lower() in self.registros and (src.startswith('0x') or src.isdigit()):
			reg = self.registros[dest.lower()]
			valor = int(src, 16) if src.startswith('0x') else int(src)
			self.ensamblador._agregar_bytes([0x83, 0xF8 + reg, valor & 0xFF])

#test r32, r32
	def procesar_test(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  TEST {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x85, 0xC0 + (src_reg << 3) + dest_reg])

# lea r32, [addr]
	def procesar_lea(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  LEA {dest}, {src}")

		if dest.lower() in self.registros and src.startswith('['):
			dest_reg = self.registros[dest.lower()]
			self.ensamblador._agregar_bytes([0x8D, 0x05 + (dest_reg << 3)])
			self.ensamblador._agregar_dword(0)

#inc r32
	def procesar_inc(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  INC {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0x40 + self.registros[reg]])

#dec r32
	def procesar_dec(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  DEC {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0x48 + self.registros[reg]])

#mul r32
	def procesar_mul(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  MUL {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0xF7, 0xE0 + self.registros[reg]])
#imul r32,r32
	def procesar_imul(self, operandos: str):
		partes = [p.strip() for p in operandos.split(',')]
		if len(partes) != 2:
			return

		dest, src = partes
		print(f"  IMUL {dest}, {src}")

		if dest.lower() in self.registros and src.lower() in self.registros:
			dest_reg = self.registros[dest.lower()]
			src_reg = self.registros[src.lower()]
			self.ensamblador._agregar_bytes([0x0F, 0xAF, 0xC0 + (dest_reg << 3) + src_reg])

#div r32
	def procesar_div(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  DIV {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0xF7, 0xF0 + self.registros[reg]])
#idiv r32
	def procesar_idiv(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  IDIV {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0xF7, 0xF8 + self.registros[reg]])

#push r32
	def procesar_push(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  PUSH {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0x50 + self.registros[reg]])
#pop r32
	def procesar_pop(self, operandos: str):
		reg = operandos.strip().lower()
		print(f"  POP {reg}")

		if reg in self.registros:
			self.ensamblador._agregar_bytes([0x58 + self.registros[reg]])
#int imm8
	def procesar_int(self, operandos: str):
		vector_str = operandos.strip()
		print(f"  INT {vector_str}")

		if vector_str.startswith('0x'):
			vector = int(vector_str, 16)
		else:
			vector = int(vector_str)

		self.ensamblador._agregar_bytes([0xCD, vector & 0xFF])
#jmp rel32
	def procesar_jmp(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JMP {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 1,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0xE9, 0x00, 0x00, 0x00, 0x00])

#je rel32
	def procesar_je(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x84, 0x00, 0x00, 0x00, 0x00])
#jne rel32
	def procesar_jne(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JNE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x85, 0x00, 0x00, 0x00, 0x00])
#jle rel32
	def procesar_jle(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JLE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x8E, 0x00, 0x00, 0x00, 0x00])
#jl rel32
	def procesar_jl(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JL {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x8C, 0x00, 0x00, 0x00, 0x00])

#jz rel32
	def procesar_jz(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JZ {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x84, 0x00, 0x00, 0x00, 0x00])
#jnz rel32
	def procesar_jnz(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JNZ {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x85, 0x00, 0x00, 0x00, 0x00])
#ja rel32
	def procesar_ja(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JA {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x87, 0x00, 0x00, 0x00, 0x00])
#jae rel32
	def procesar_jae(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JAE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x83, 0x00, 0x00, 0x00, 0x00])

#jb rel32
	def procesar_jb(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JB {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x82, 0x00, 0x00, 0x00, 0x00])
#jbe rel32
	def procesar_jbe(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JBE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x86, 0x00, 0x00, 0x00, 0x00])
#jg rel32
	def procesar_jg(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JG {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x8F, 0x00, 0x00, 0x00, 0x00])
#jge rel32
	def procesar_jge(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  JGE {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 2,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0x0F, 0x8D, 0x00, 0x00, 0x00, 0x00])
#call rel32
	def procesar_call(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  CALL {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 1,
			'tipo': 'rel32',
			'tamaño': 4
		})

		self.ensamblador._agregar_bytes([0xE8, 0x00, 0x00, 0x00, 0x00])

#loop rel8
	def procesar_loop(self, operandos: str):
		etiqueta = operandos.strip()
		print(f"  LOOP {etiqueta}")

		if etiqueta not in self.ensamblador.referencias_pendientes:
			self.ensamblador.referencias_pendientes[etiqueta] = []

		self.ensamblador.referencias_pendientes[etiqueta].append({
			'posicion': len(self.ensamblador.codigo_hex) + 1,
			'tipo': 'rel8',
			'tamaño': 1
		})

		self.ensamblador._agregar_bytes([0xE2, 0x00])
#ret
	def procesar_ret(self):
		print("  RET")
		self.ensamblador._agregar_bytes([0xC3])
#nop
	def procesar_nop(self):
		print("  NOP")
		self.ensamblador._agregar_bytes([0x90])
