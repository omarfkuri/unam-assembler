from time import perf_counter
from os import makedirs

from asm import Asm

def main():

	IN_DIR = "files"
	OUT_DIR = "out"
	NAME = "fib"

	IN = f"{IN_DIR}/{NAME}.asm"
	OUT = f"{OUT_DIR}/{NAME}"

	OUT_REF = f"{OUT}.ref.txt"
	OUT_SIM = f"{OUT}.sim.txt"

	makedirs(OUT_DIR, exist_ok=True)

	asm = Asm()
	print()
	print(f"Ensamblando {IN}...")
	start = perf_counter()
	result = asm.assemble(IN)
	end = perf_counter()
	print(f"Listo en {(end - start) * 1000:.2f}ms")
	print()

	with open(OUT, "w") as file:
		file.write(result.machineCode)

	print(f"Código escrito a {OUT}")

	with open(OUT_REF, "w") as file:
		file.write(str(result.referenceTable))

	print(f"Tabla de referencias escrita a {OUT_REF}")

	with open(OUT_SIM, "w") as file:
		file.write(str(result.symbolTable))

	print(f"Tabla de símbolos escrita a {OUT_SIM}")

if __name__ == "__main__":
	main()