"""Ensamblador de una pasada IA-32 - Traducción de C++"""

import sys
from asm.common import *
from .InstructionProcessor import InstructionProcessor


class EnsambladorIA32(AssemblerI):
	"""
	Ensamblador de una pasada para IA-32.
	Basado en traducción de C++ con mejoras para el proyecto.
	"""

	def __init__(self):
		super().__init__("1 pasada")
		# Tabla de Símbolos: {nombre_etiqueta: direccion_entera}
		self.tabla_simbolos = {}
		# Referencias Pendientes: {nombre_etiqueta: [posicion_codigo1, posicion_codigo2, ...]}
		self.referencias_pendientes = {}
		# Código Máquina: lista de enteros (bytes)
		self.codigo_hex = []
		# Contador de Posición: dirección actual de la instrucción
		self.contador_posicion = 0
		# Sección actual
		self.seccion_actual = None
		# Desplazamientos de secciones
		self.offset_data = 0x0000
		self.offset_text = 0x1000
		# Procesador de instrucciones
		self.instruction_processor = InstructionProcessor(self)

	def assemble(self, filename: str) -> Result:
		"""Ensambla un archivo en una pasada"""
		try:
			print("Procesando archivo en una pasada...")
			self.ensamblar(filename)
			self.resolver_referencias_pendientes()
			
			# Convertir código hex a string
			codigo_str = self._generar_hex_string()
			
			# Crear tabla de referencias (compatible con ReferenceTable)
			tabla_referencias = ReferenceTable()
			for etiqueta, referencias in self.referencias_pendientes.items():
				for ref in referencias:
					tabla_referencias.add_reference(
						etiqueta,
						ref['posicion'],
						ref['tipo'],
						ref['tamaño']
					)
			
			# Crear tabla de símbolos con SymbolTable
			sym_table = SymbolTable()
			for nombre, direccion in self.tabla_simbolos.items():
				sym_table.add_symbol(nombre, direccion)
			
			return Result(sym_table, tabla_referencias, codigo_str)
			
		except IOError as e:
			sys.stderr.write(f"Error: no se pudo abrir {filename}\n")
			return Result(SymbolTable(), ReferenceTable(), "")

	def limpiar_linea(self, linea: str) -> str:
		"""Quitar comentarios (;) y espacios en blanco"""
		# Remover comentarios
		if ';' in linea:
			linea = linea[:linea.index(';')]
		
		linea = linea.strip()
		return linea

	def es_etiqueta(self, linea: str) -> bool:
		"""Verificar si la línea es una etiqueta (termina en ':')"""
		linea = linea.strip()
		return linea.endswith(':') and len(linea) > 1

	def es_directiva_seccion(self, linea: str) -> bool:
		"""Verificar si es una directiva section"""
		return linea.lower().startswith('section')

	def procesar_etiqueta(self, etiqueta: str):
		"""Añadir la etiqueta a tabla_simbolos con la dirección actual"""
		self.tabla_simbolos[etiqueta] = self.contador_posicion
		print(f"  Etiqueta '{etiqueta}' @ 0x{self.contador_posicion:04X}")

	def procesar_directiva_seccion(self, linea: str):
		"""Procesa directiva section"""
		if '.data' in linea.lower():
			self.seccion_actual = 'data'
			self.contador_posicion = self.offset_data
			print(f"Sección .data @ 0x{self.contador_posicion:04X}")
		elif '.text' in linea.lower():
			self.seccion_actual = 'text'
			self.contador_posicion = self.offset_text
			print(f"Sección .text @ 0x{self.contador_posicion:04X}")

	def procesar_instruccion(self, linea: str):
		"""Procesar instrucción y generar código"""
		tokens = linea.split()
		if not tokens:
			return

		mnemonica = tokens[0].lower()
		operandos = ' '.join(tokens[1:]) if len(tokens) > 1 else ""

		# Verificar si es declaración de datos
		if len(tokens) >= 2 and tokens[1].lower() in ['db', 'dw', 'dd']:
			self._procesar_declaracion_datos(linea)
			return

		# Delegar al procesador de instrucciones
		self.instruction_processor.procesar(mnemonica, operandos)

	def _procesar_declaracion_datos(self, linea: str):
		"""Procesa declaraciones de datos: label dd/dw/db valor"""
		tokens = linea.split()
		if len(tokens) < 2:
			return

		label = tokens[0]
		directive = tokens[1].lower()
		valor_str = ' '.join(tokens[2:]) if len(tokens) > 2 else "0"

		# Registrar etiqueta
		self.tabla_simbolos[label] = self.contador_posicion
		print(f"  Dato '{label}' ({directive}) @ 0x{self.contador_posicion:04X}")

		# Tamaño según directiva
		size_map = {'db': 1, 'dw': 2, 'dd': 4}
		size = size_map.get(directive, 4)

		# Generar bytecode para el valor
		try:
			valor = int(valor_str, 16) if valor_str.startswith('0x') else int(valor_str)
		except:
			valor = 0

		# Agregar bytes según el tamaño
		for i in range(size):
			self._agregar_bytes([(valor >> (i * 8)) & 0xFF])

	def _agregar_bytes(self, bytecode: list):
		"""Añade bytecode al código hexadecimal"""
		self.codigo_hex.extend(bytecode)
		self.contador_posicion += len(bytecode)

	def _agregar_dword(self, valor: int):
		"""Añade un DWORD (4 bytes) en formato little-endian"""
		self._agregar_bytes([
			valor & 0xFF,
			(valor >> 8) & 0xFF,
			(valor >> 16) & 0xFF,
			(valor >> 24) & 0xFF
		])

	def ensamblar(self, archivo_entrada: str):
		"""Lee el archivo y procesa línea por línea"""
		try:
			with open(archivo_entrada, 'r') as f:
				for numero_linea, linea in enumerate(f, 1):
					linea_limpia = self.limpiar_linea(linea)
					
					if not linea_limpia:
						continue

					if self.es_directiva_seccion(linea_limpia):
						self.procesar_directiva_seccion(linea_limpia)
					elif self.es_etiqueta(linea_limpia):
						etiqueta = linea_limpia.strip(':')
						self.procesar_etiqueta(etiqueta)
					elif linea_limpia.lower().startswith('global'):
						continue
					else:
						self.procesar_instruccion(linea_limpia)

		except IOError:
			sys.stderr.write(f"Error: no se pudo abrir {archivo_entrada}\n")

	def resolver_referencias_pendientes(self):
		"""Itera y parchea las direcciones de salto y referencias"""
		print("Resolviendo referencias adelantadas...")

		resolved_count = 0
		unresolved_etiquetas = []

		for etiqueta, referencias in self.referencias_pendientes.items():
			if etiqueta in self.tabla_simbolos:
				direccion_destino = self.tabla_simbolos[etiqueta]

				for ref in referencias:
					posicion = ref['posicion']
					tipo = ref['tipo']

					if tipo == 'rel32':
						# El offset es relativo al siguiente byte después del salto
						offset = direccion_destino - (posicion + 4)
						self.codigo_hex[posicion] = offset & 0xFF
						self.codigo_hex[posicion + 1] = (offset >> 8) & 0xFF
						self.codigo_hex[posicion + 2] = (offset >> 16) & 0xFF
						self.codigo_hex[posicion + 3] = (offset >> 24) & 0xFF
						resolved_count += 1

					elif tipo == 'rel8':
						# El offset es relativo al siguiente byte después del salto
						offset = direccion_destino - (posicion + 1)
						self.codigo_hex[posicion] = offset & 0xFF
						resolved_count += 1

			else:
				unresolved_etiquetas.append(etiqueta)

		if resolved_count > 0:
			print(f"  {resolved_count} referencias resueltas")

		if unresolved_etiquetas:
			print(f"  Advertencia: {len(unresolved_etiquetas)} etiquetas sin resolver:")
			for etiqueta in unresolved_etiquetas:
				print(f"    - {etiqueta}")

	def _generar_hex_string(self) -> str:
		"""Convierte código hex a string para salida"""
		lines = []
		for i in range(0, len(self.codigo_hex), 16):
			chunk = self.codigo_hex[i:i+16]
			hex_str = ' '.join(f'{b:02X}' for b in chunk)
			lines.append(hex_str)
		return '\n'.join(lines) if lines else ""


# Alias para compatibilidad
OnePassAssembler = EnsambladorIA32
