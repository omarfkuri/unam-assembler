from os import makedirs

from asm import *

NAME = "fib"
IN_DIR = "files"
OUT_DIR_1 = "out/one_pass"
OUT_DIR_2 = "out/two_pass"

# Se busca un archivo llamado "{IN_DIR}/{NAME}.asm"
# y se produce a "{OUT_DIR_1}" el código de 1
# pasada, y a "{OUT_DIR_2}" el código de 2 pasadas.

def main():
	makedirs(OUT_DIR_1, exist_ok=True)
	makedirs(OUT_DIR_2, exist_ok=True)

	asm = OnePassAssembler()
	asm.run(NAME, IN_DIR, OUT_DIR_1)

	asm = TwoPassAssembler()
	asm.run(NAME, IN_DIR, OUT_DIR_2)

if __name__ == "__main__":
	main()