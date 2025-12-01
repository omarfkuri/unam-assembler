from os import makedirs
from time import perf_counter
from .Result import *

class AssemblerI:

	def __init__(self, name: str):
		self.name = name

	def assemble(self, filename: str) -> Result:
		raise RuntimeError(f"Assemble not implemented for {self}")

	def run(self, name: str, in_dir: str, out_dir: str):

		in_file = f"{in_dir}/{name}.asm"

		makedirs(out_dir, exist_ok=True)

		print()
		print(f"Ensamblando ({self.name}): {in_file}...")
		start = perf_counter()
		result = self.assemble(in_file)
		end = perf_counter()
		print(f"Listo en {(end - start) * 1000:.2f}ms")
		print()

		self.write(result, name, out_dir)

	def write(self, result: Result, name: str, out_dir: str):

		out_file = f"{out_dir}/{name}.hex"
		out_ref  = f"{out_dir}/{name}.ref.txt"
		out_sim  = f"{out_dir}/{name}.sim.txt"

		with open(out_file, "w") as file:
			file.write(result.machineCode)

		print(f"Código escrito a {out_file}")

		with open(out_ref, "w") as file:
			file.write(str(result.referenceTable))

		print(f"Tabla de referencias escrita a {out_ref}")

		with open(out_sim, "w") as file:
			file.write(str(result.symbolTable))

		print(f"Tabla de símbolos escrita a {out_sim}")