import sys
from asm.common import *
from .InstructionProcessor import InstructionProcessor


class OnePassAssembler(AssemblerI):

	def __init__(self):
		super().__init__("1 pasada")
		self.tabla_simbolos = {}
		self.referencias_pendientes = {}
		self.codigo_hex = []
		#dirección actual
		self.contador_posicion = 0
		# Sección actual
		self.seccion_actual = None
		#desplazamientos
		self.offset_data = 0x0000
		self.offset_text = 0x1000
		#procesa las instrucciones
		self.instruction_processor = InstructionProcessor(self)

	def assemble(self, filename: str) -> Result:
		try:
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
			
			#creamos la tabla de símbolos
			sym_table = SymbolTable()
			for nombre, direccion in self.tabla_simbolos.items():
				sym_table.add_symbol(nombre, direccion)
			
			return Result(sym_table, tabla_referencias, codigo_str)
			
		except IOError as e:
			sys.stderr.write(f"Error: no se pudo abrir {filename}\n")
			return Result(SymbolTable(), ReferenceTable(), "")

	def limpiar_linea(self, linea: str) -> str:
		#esta es pa los comentarios
		if ';' in linea:
			linea = linea[:linea.index(';')]
		
		linea = linea.strip()
		return linea

	#etiquetas
	def es_etiqueta(self, linea: str) -> bool:
		linea = linea.strip()
		return linea.endswith(':') and len(linea) > 1

	def es_directiva_seccion(self, linea: str) -> bool:
		return linea.lower().startswith('section')

	def procesar_etiqueta(self, etiqueta: str):
		self.tabla_simbolos[etiqueta] = self.contador_posicion
		print(f"  Etiqueta '{etiqueta}' @ 0x{self.contador_posicion:04X}")

	def procesar_directiva_seccion(self, linea: str):
		if '.data' in linea.lower():
			self.seccion_actual = 'data'
			self.contador_posicion = self.offset_data
			print(f"Sección .data @ 0x{self.contador_posicion:04X}")
		elif '.text' in linea.lower():
			self.seccion_actual = 'text'
			self.contador_posicion = self.offset_text
			print(f"Sección .text @ 0x{self.contador_posicion:04X}")

	def procesar_instruccion(self, linea: str):
		tokens = linea.split()
		if not tokens:
			return

		mnemonica = tokens[0].lower()
		operandos = ' '.join(tokens[1:]) if len(tokens) > 1 else ""

		#declaraciones de datos
		if len(tokens) >= 2 and tokens[1].lower() in ['db', 'dw', 'dd']:
			self._procesar_declaracion_datos(linea)
			return

		self.instruction_processor.procesar(mnemonica, operandos)

#para declaraciones de datos
	def _procesar_declaracion_datos(self, linea: str):
		tokens = linea.split()
		if len(tokens) < 2:
			return

		label = tokens[0]
		directive = tokens[1].lower()
		valor_str = ' '.join(tokens[2:]) if len(tokens) > 2 else "0"

		self.tabla_simbolos[label] = self.contador_posicion
		print(f"  Dato '{label}' ({directive}) @ 0x{self.contador_posicion:04X}")

		#tamaños de datos
		size_map = {'db': 1, 'dw': 2, 'dd': 4}
		size = size_map.get(directive, 4)

#ge ramos el byte code
		try:
			valor = int(valor_str, 16) if valor_str.startswith('0x') else int(valor_str)
		except:
			valor = 0

		#dependiendo del tamaño asignamos valor 
		for i in range(size):
			self._agregar_bytes([(valor >> (i * 8)) & 0xFF])

#añadimos bytes al código
	def _agregar_bytes(self, bytecode: list):
		self.codigo_hex.extend(bytecode)
		self.contador_posicion += len(bytecode)
#se añade un dword
	def _agregar_dword(self, valor: int):
		self._agregar_bytes([
			valor & 0xFF,
			(valor >> 8) & 0xFF,
			(valor >> 16) & 0xFF,
			(valor >> 24) & 0xFF
		])

#lee ek archivo y se procesa linea por linea
	def ensamblar(self, archivo_entrada: str):
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
			sys.stderr.write(f"Error al abrir el archivo: {archivo_entrada}\n")

	def resolver_referencias_pendientes(self):
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
						#el offset es relativo al siguiente byte después del salto
						offset = direccion_destino - (posicion + 4)
						self.codigo_hex[posicion] = offset & 0xFF
						self.codigo_hex[posicion + 1] = (offset >> 8) & 0xFF
						self.codigo_hex[posicion + 2] = (offset >> 16) & 0xFF
						self.codigo_hex[posicion + 3] = (offset >> 24) & 0xFF
						resolved_count += 1

					elif tipo == 'rel8':
						#el offset es relativo al siguiente byte después del salto
						offset = direccion_destino - (posicion + 1)
						self.codigo_hex[posicion] = offset & 0xFF
						resolved_count += 1

			else:
				unresolved_etiquetas.append(etiqueta)

		if resolved_count > 0:
			print(f"  {resolved_count} referencias adelantadas resueltas")

		if unresolved_etiquetas:
			print(f"  Advertencia: {len(unresolved_etiquetas)} etiquetas sin resolver:")
			for etiqueta in unresolved_etiquetas:
				print(f"    - {etiqueta}")

#Convertimos el código hex a string
	def _generar_hex_string(self) -> str:
		lines = []
		for i in range(0, len(self.codigo_hex), 16):
			chunk = self.codigo_hex[i:i+16]
			hex_str = ' '.join(f'{b:02X}' for b in chunk)
			lines.append(hex_str)
		return '\n'.join(lines) if lines else ""
