from os import makedirs

from asm import *
from asm.two_pass.two_pass import TwoPassAssembler 

NAME = "test3"
IN_DIR = "files"
OUT_DIR_1 = "out/one_pass"
OUT_DIR_2 = "out/two_pass"

def main():
	makedirs(OUT_DIR_1, exist_ok=True)
	makedirs(OUT_DIR_2, exist_ok=True)

	print("--- Ejecutando One Pass ---")
	asm = OnePassAssembler()
	asm.run(NAME, IN_DIR, OUT_DIR_1)

	print("\n--- Ejecutando Two Pass ---")
	asm = TwoPassAssembler()
	asm.run(NAME, IN_DIR, OUT_DIR_2)

if __name__ == "__main__":
	main()