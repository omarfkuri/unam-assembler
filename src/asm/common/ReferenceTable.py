class ReferenceTable:
    def __init__(self):
        # Diccionario que mapea: Nombre del Símbolo -> Lista de direcciones donde se usa
        self.references: dict[str, list[int]] = {}

    def add_usage(self, name: str, address: int):
        """Registra que el símbolo 'name' fue usado en la dirección 'address'."""
        if name not in self.references:
            self.references[name] = []
        self.references[name].append(address)

    def __str__(self):
        if not self.references:
            return "Tabla de referencias: (Vacía)"

        lines = ["Tabla de referencias:"]
        lines.append("-" * 80)
        lines.append(f"{'Símbolo':<20} {'Direcciones de uso (Hex)'}")
        lines.append("-" * 80)

        for name, addresses in sorted(self.references.items()):
            # Formateamos las direcciones como una lista separada por comas: 0x00001000, 0x00001005...
            addr_str = ", ".join([f"0x{addr:08X}" for addr in addresses])
            lines.append(f"{name:<20} {addr_str}")

        lines.append("-" * 80)
        lines.append(f"Total: {len(self.references)} símbolos referenciados")
        
        return "\n".join(lines)