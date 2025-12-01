
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