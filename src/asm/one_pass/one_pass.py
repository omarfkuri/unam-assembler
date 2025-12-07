from typing import cast
from asm.common import *

try:
    from asm.two_pass.parser.Instruction import *
except ImportError:
    from asm.two_pass.Instruction import *

from asm.two_pass.parser import Parser

REGISTERS = {
    'eax': 0, 'ecx': 1, 'edx': 2, 'ebx': 3, 'esp': 4, 'ebp': 5, 'esi': 6, 'edi': 7,
    'ax': 0,  'cx': 1,  'dx': 2,  'bx': 3,  'sp': 4,  'bp': 5,  'si': 6,  'di': 7,
    'al': 0,  'cl': 1,  'dl': 2,  'bl': 3,  'ah': 4,  'ch': 5,  'dh': 6,  'bh': 7
}

class OnePassAssembler(AssemblerI):

    def __init__(self):
        super().__init__("1 pasada")
        self.parser_helper = Parser()
        self.symbol_table = SymbolTable()
        self.ref_table = ReferenceTable()
        self.current_address = 0x1000
        self.code_bytes = bytearray()
        self.pending_patches: dict[str, list[tuple[int, str, int]]] = {}

    def assemble(self, filename) -> Result:
        self.symbol_table = SymbolTable()
        self.ref_table = ReferenceTable()
        self.code_bytes = bytearray()
        self.pending_patches = {}
        self.current_address = 0x1000

        try:
            with open(filename, "r", encoding="utf-8") as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {filename}")
            return Result(self.symbol_table, self.ref_table, "")

        for line in lines:
            self._process_line(line)

        hex_code = " ".join(f"{b:02X}" for b in self.code_bytes)
        return Result(self.symbol_table, self.ref_table, hex_code)

    def _process_line(self, line: str):
        code = line.strip()
        if not code or code.startswith(';'): return
        if ';' in code: code = code[:code.index(';')].strip()
        
        tokens = code.split()
        if not tokens: return

        if code.endswith(':'):
            label_name = code[:-1]
            self._define_label(label_name)
            return

        if tokens[0].lower() in ['section', 'global']: return

        if len(tokens) >= 2 and tokens[1].lower() in ['dd', 'dw', 'db']:
            label = tokens[0]
            directive = tokens[1].lower()
            value = ' '.join(tokens[2:]) if len(tokens) > 2 else ""
            
            self._define_label(label)
            data_bytes = self._encode_data_bytes(directive, value)
            self._emit(data_bytes)
            return

        try:
            inst = self.parser_helper._parseInstruction(code)
            self._generate_inst_code(inst)
        except Exception as e:
            pass

    def _generate_inst_code(self, instruction: Instruction):
        opcode = []
        
        match instruction:
            # movimientos
            case MoveInstruction():
                if isinstance(instruction.dest, MemoryExpression):
                    opcode = [0x89] 
                    modrm, addr_bytes = self._encode_mem_operand(instruction.src, instruction.dest)
                    opcode.append(modrm)
                    opcode.extend(addr_bytes)
                elif isinstance(instruction.src, MemoryExpression):
                    opcode = [0x8B]
                    modrm, addr_bytes = self._encode_mem_operand(instruction.dest, instruction.src)
                    opcode.append(modrm)
                    opcode.extend(addr_bytes)
                elif isinstance(instruction.src, IntegerExpression):
                     reg_id = self._get_reg_id(instruction.dest)
                     opcode = [0xB8 + reg_id]
                     opcode.extend(instruction.src.value.to_bytes(4, 'little'))
                else:
                    opcode = [0x89, self._encode_reg_reg_byte(instruction.dest, instruction.src)]

            case MovzxInstruction():
                opcode = [0x0F, 0xB6, self._encode_reg_reg_byte(instruction.dest, instruction.src)]
            
            case LeaInstruction():
                opcode = [0x8D]
                modrm, addr_bytes = self._encode_mem_operand(instruction.reg, instruction.mem)
                opcode.append(modrm)
                opcode.extend(addr_bytes)

            case XchgInstruction():
                opcode = [0x87, self._encode_reg_reg_byte(instruction.op1, instruction.op2)]

            # pila 
            case PushInstruction():
                # 50+rd (PUSH r32)
                reg_id = self._get_reg_id(instruction.op)
                opcode = [0x50 + reg_id]

            case PopInstruction():
                # 58+rd (POP r32)
                reg_id = self._get_reg_id(instruction.op)
                opcode = [0x58 + reg_id]

            # aritmética
            case AddInstruction():
                opcode = [0x01, self._encode_reg_reg_byte(instruction.dest, instruction.src)]

            case SubInstruction():
                opcode = [0x29, self._encode_reg_reg_byte(instruction.dest, instruction.src)]

            case MulInstruction():
                reg_id = self._get_reg_id(instruction.op)
                modrm = 0xE0 | reg_id # 11 100 reg
                opcode = [0xF7, modrm]

            case DivInstruction():
                reg_id = self._get_reg_id(instruction.op)
                modrm = 0xF0 | reg_id # 11 110 reg
                opcode = [0xF7, modrm]

            case DecInstruction():
                reg_id = self._get_reg_id(instruction.op)
                opcode = [0x48 + reg_id] # 48+rd

            case IncInstruction():
                reg_id = self._get_reg_id(instruction.op)
                opcode = [0x40 + reg_id] # 40+rd
            
            # lógica 
            case AndInstruction():
                opcode = [0x21, self._encode_reg_reg_byte(instruction.dest, instruction.src)]
            
            case OrInstruction():
                opcode = [0x09, self._encode_reg_reg_byte(instruction.dest, instruction.src)]
            
            case XorInstruction():
                opcode = [0x31, self._encode_reg_reg_byte(instruction.dest, instruction.src)]

            case TestInstruction():
                opcode = [0x85, self._encode_reg_reg_byte(instruction.op1, instruction.op2)]

            # cmp 
            case CmpInstruction():
                if isinstance(instruction.op2, IntegerExpression):
                    reg_id = self._get_reg_id(instruction.op1)
                    modrm = 0xF8 | reg_id 
                    opcode = [0x83, modrm, instruction.op2.value & 0xFF]
                elif isinstance(instruction.op2, MemoryExpression):
                    opcode = [0x3B]
                    modrm, addr_bytes = self._encode_mem_operand(instruction.op1, instruction.op2)
                    opcode.append(modrm)
                    opcode.extend(addr_bytes)
                else:
                    opcode = [0x39, self._encode_reg_reg_byte(instruction.op1, instruction.op2)]

            # saltos y control
            case LoopInstruction(): opcode = [0xE2, self._encode_rel_jump(instruction.label)]
            case JmpInstruction(): opcode = [0xEB, self._encode_rel_jump(instruction.label)]
            
            # Saltos Condicionales
            case JeInstruction() | JzInstruction():   opcode = [0x74, self._encode_rel_jump(instruction.label)]
            case JneInstruction() | JnzInstruction(): opcode = [0x75, self._encode_rel_jump(instruction.label)]
            case JlInstruction():                     opcode = [0x7C, self._encode_rel_jump(instruction.label)]
            case JleInstruction():                    opcode = [0x7E, self._encode_rel_jump(instruction.label)]
            case JgInstruction():                     opcode = [0x7F, self._encode_rel_jump(instruction.label)]
            case JgeInstruction():                    opcode = [0x7D, self._encode_rel_jump(instruction.label)]
            case JaInstruction():                     opcode = [0x77, self._encode_rel_jump(instruction.label)]
            case JaeInstruction():                    opcode = [0x73, self._encode_rel_jump(instruction.label)]
            case JbInstruction():                     opcode = [0x72, self._encode_rel_jump(instruction.label)]
            case JbeInstruction():                    opcode = [0x76, self._encode_rel_jump(instruction.label)]

            case CallInstruction():
                opcode = [0xE8]
                offset_bytes = self._encode_call_offset(instruction.label)
                opcode.extend(offset_bytes)

            case RetInstruction():
                opcode = [0xC3]

            case IntInstruction():
                val = self._get_value_safe(instruction.imm8)
                opcode = [0xCD, val]
            
            case NopInstruction():
                opcode = [0x90]
            
            case _:
                opcode = [0x90]

        self._emit(opcode)

    # metodos auxiliares

    def _define_label(self, label: str):
        if self.symbol_table.has_symbol(label): return
        address = self.current_address
        self.symbol_table.add_symbol(label, address)
        if label in self.pending_patches:
            for patch_pos, patch_type, origin_addr in self.pending_patches[label]:
                self._apply_patch(patch_pos, patch_type, origin_addr, address)
            del self.pending_patches[label]

    def _emit(self, bytes_list: list[int] | bytearray):
        self.code_bytes.extend(bytes_list)
        self.current_address += len(bytes_list)

    def _encode_rel_jump(self, label: str) -> int:
        # Salto corto de 8 bits
        self._add_ref(label)
        if self.symbol_table.has_symbol(label):
            target = self.symbol_table.get_address(label)
            offset = target - (self.current_address + 2)
            return offset & 0xFF
        else:
            patch_pos = len(self.code_bytes) + 1
            self._register_patch(label, patch_pos, "REL8", self.current_address)
            return 0x00

    def _encode_call_offset(self, label: str) -> list[int]:
        # Salto relativo de 32 bits para CALL
        self._add_ref(label)
        if self.symbol_table.has_symbol(label):
            target = self.symbol_table.get_address(label)
            # Offset = Target - (Current + 5 bytes de instr)
            offset = target - (self.current_address + 5)
            return list(offset.to_bytes(4, 'little', signed=True))
        else:
            patch_pos = len(self.code_bytes) + 1
            self._register_patch(label, patch_pos, "REL32", self.current_address)
            return [0, 0, 0, 0]

    def _encode_mem_operand(self, reg_expr: Expression, mem_expr: MemoryExpression) -> tuple[int, list[int]]:
        dest_reg = self._get_reg_id(reg_expr)
        modrm = (dest_reg << 3) | 5
        addr_bytes = [0, 0, 0, 0]
        if isinstance(mem_expr.address, IdentifierExpression):
            label = mem_expr.address.name
            self._add_ref(label)
            if self.symbol_table.has_symbol(label):
                addr = self.symbol_table.get_address(label)
                addr_bytes = list(addr.to_bytes(4, 'little'))
            else:
                patch_pos = len(self.code_bytes) + 2 
                self._register_patch(label, patch_pos, "ABS32", 0)
        return modrm, addr_bytes

    def _register_patch(self, label: str, pos: int, type: str, origin: int):
        if label not in self.pending_patches:
            self.pending_patches[label] = []
        self.pending_patches[label].append((pos, type, origin))

    def _apply_patch(self, pos: int, type: str, origin: int, target: int):
        if type == "REL8":
            offset = target - (origin + 2) 
            self.code_bytes[pos] = offset & 0xFF
        elif type == "REL32": # Para CALL
            offset = target - (origin + 5)
            bytes_val = offset.to_bytes(4, 'little', signed=True)
            for i in range(4): self.code_bytes[pos + i] = bytes_val[i]
        elif type == "ABS32":
            bytes_val = target.to_bytes(4, 'little')
            for i in range(4): self.code_bytes[pos + i] = bytes_val[i]

    def _encode_reg_reg_byte(self, dest, src) -> int:
        return 0xC0 | (self._get_reg_id(src) << 3) | self._get_reg_id(dest)

    def _get_reg_id(self, expr) -> int:
        if isinstance(expr, IdentifierExpression): return REGISTERS.get(expr.name.lower(), 0)
        return 0

    def _encode_data_bytes(self, directive, value_str) -> list[int]:
        try: val = int(value_str)
        except: val = 0
        if directive == 'db': return [val & 0xFF]
        elif directive == 'dw': return list(val.to_bytes(2, 'little'))
        elif directive == 'dd': return list(val.to_bytes(4, 'little'))
        return []

    def _get_value_safe(self, expr):
        if isinstance(expr, IntegerExpression): return expr.value
        return 0

    def _add_ref(self, label: str):
        if hasattr(self.ref_table, 'add_usage'): self.ref_table.add_usage(label, self.current_address)