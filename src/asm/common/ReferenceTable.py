
class ReferenceTable:
	def __init__(self):
		self.references = {}  # {etiqueta: [{'posicion': int, 'tipo': str, 'tamaño': int}, ...]}

	def add_reference(self, etiqueta: str, posicion: int, tipo: str, tamaño: int):
		"""Agrega una referencia pendiente"""
		if etiqueta not in self.references:
			self.references[etiqueta] = []
		self.references[etiqueta].append({
			'posicion': posicion,
			'tipo': tipo,
			'tamaño': tamaño
		})

	def __str__(self):
		if not self.references:
			return "Tabla de referencias:\n--\nSin referencias pendientes"
		
		lines = ["Tabla de referencias:"]
		lines.append("-" * 60)
		lines.append(f"{'Etiqueta':<20} {'Posición':>12} {'Tipo':>12} {'Tamaño':>8}")
		lines.append("-" * 60)
		
		total_refs = 0
		for etiqueta, refs in sorted(self.references.items()):
			for ref in refs:
				lines.append(f"{etiqueta:<20} 0x{ref['posicion']:08X} {ref['tipo']:>12} {ref['tamaño']:>8}")
				total_refs += 1
		
		lines.append("-" * 60)
		lines.append(f"Total: {total_refs} referencias")
		
		return "\n".join(lines)
