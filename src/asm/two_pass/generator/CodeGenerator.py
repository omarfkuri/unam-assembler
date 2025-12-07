import sys
try:
    from asm.two_pass.parser.Instruction import *
except ImportError:
    from asm.two_pass.Instruction import *
from asm.two_pass.parser import Parser
from asm.common import *

REGISTERS = {
    'eax': 0, 'ecx': 1, 'edx': 2, 'ebx': 3, 'esp': 4, 'ebp': 5, 'esi': 6, 'edi': 7,
    'ax': 0,  'cx': 1,  'dx': 2,  'bx': 3,  'sp': 4,  'bp': 5,  'si': 6,  'di': 7,
    'al': 0,  'cl': 1,  'dl': 2,  'bl': 3,  'ah': 4,  'ch': 5,  'dh': 6,  'bh': 7
}

class CodeGeneratorResult:
    def __init__(self, referenceTable: ReferenceTable, code: str):
        self.referenceTable = referenceTable
        self.code = code

class CodeGenerator:
    def __init__(self):
        self.referenceTable = None
        self.symbol_table = None 
        self.current_address = 0

    def generateCode(self, instructions: list[Instruction], symbol_table: SymbolTable) -> CodeGeneratorResult:
        self.referenceTable = ReferenceTable()
        self.symbol_table = symbol_table 
        self.current_address = 0x1000 
        code = self._processInstructions(instructions)
        return CodeGeneratorResult(self.referenceTable, code)

    def _processInstructions(self, instructions: list[Instruction]) -> str:
        code_lines = []
        for instruction in instructions:
            inst_hex = "" 
            match instruction:
                case MoveInstruction():
                    if isinstance(instruction.src, MemoryExpression):
                        inst_hex = self._encode_mem_op("8B", instruction.dest, instruction.src)
                    elif isinstance(instruction.dest, MemoryExpression):
                        inst_hex = self._encode_mem_op("89", instruction.src, instruction.dest)
                    elif isinstance(instruction.src, IntegerExpression):
                        reg_id = self._get_reg_value(instruction.dest)
                        val_hex = instruction.src.value.to_bytes(4, 'little').hex().upper()
                        inst_hex = f"{0xB8 + reg_id:02X} {val_hex[0:2]} {val_hex[2:4]} {val_hex[4:6]} {val_hex[6:8]}"
                    else:
                        inst_hex = f"89 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                
                case MovzxInstruction(): inst_hex = f"0F B6 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case LeaInstruction():   inst_hex = self._encode_mem_op("8D", instruction.reg, instruction.mem)
                case XchgInstruction():  inst_hex = f"87 {self._encode_reg_reg(instruction.op1, instruction.op2)}"
                case PushInstruction():  inst_hex = f"{0x50 + self._get_reg_value(instruction.op):02X}"
                case PopInstruction():   inst_hex = f"{0x58 + self._get_reg_value(instruction.op):02X}"

                case AddInstruction(): inst_hex = f"01 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case SubInstruction(): inst_hex = f"29 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case MulInstruction(): inst_hex = f"F7 {0xE0 | self._get_reg_value(instruction.op):02X}"
                case DivInstruction(): inst_hex = f"F7 {0xF0 | self._get_reg_value(instruction.op):02X}"
                case IncInstruction(): inst_hex = f"{0x40 + self._get_reg_value(instruction.op):02X}"
                case DecInstruction(): inst_hex = f"{0x48 + self._get_reg_value(instruction.op):02X}"

                case AndInstruction(): inst_hex = f"21 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case OrInstruction():  inst_hex = f"09 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case XorInstruction(): inst_hex = f"31 {self._encode_reg_reg(instruction.dest, instruction.src)}"
                case TestInstruction(): inst_hex = f"85 {self._encode_reg_reg(instruction.op1, instruction.op2)}"

                case CmpInstruction():
                    if isinstance(instruction.op2, IntegerExpression):
                        modrm = 0xF8 | self._get_reg_value(instruction.op1)
                        inst_hex = f"83 {modrm:02X} {instruction.op2.value & 0xFF:02X}"
                    elif isinstance(instruction.op2, MemoryExpression):
                        inst_hex = self._encode_mem_op("3B", instruction.op1, instruction.op2)
                    else:
                        inst_hex = f"39 {self._encode_reg_reg(instruction.op1, instruction.op2)}"

                case LoopInstruction(): inst_hex = self._handle_jump("E2", instruction.label)
                case JmpInstruction():  inst_hex = self._handle_jump("EB", instruction.label)
                case JeInstruction() | JzInstruction():   inst_hex = self._handle_jump("74", instruction.label)
                case JneInstruction() | JnzInstruction(): inst_hex = self._handle_jump("75", instruction.label)
                case JlInstruction():  inst_hex = self._handle_jump("7C", instruction.label)
                case JleInstruction(): inst_hex = self._handle_jump("7E", instruction.label)
                case JgInstruction():  inst_hex = self._handle_jump("7F", instruction.label)
                case JgeInstruction(): inst_hex = self._handle_jump("7D", instruction.label)
                case JaInstruction():  inst_hex = self._handle_jump("77", instruction.label)
                case JaeInstruction(): inst_hex = self._handle_jump("73", instruction.label)
                case JbInstruction():  inst_hex = self._handle_jump("72", instruction.label)
                case JbeInstruction(): inst_hex = self._handle_jump("76", instruction.label)

                case CallInstruction():
                    self._add_ref(instruction.label)
                    target = self.symbol_table.get_address(instruction.label) if self.symbol_table else 0
                    offset = target - (self.current_address + 5)
                    off_hex = offset.to_bytes(4, 'little', signed=True).hex().upper()
                    inst_hex = f"E8 {off_hex[0:2]} {off_hex[2:4]} {off_hex[4:6]} {off_hex[6:8]}"
                
                case RetInstruction(): inst_hex = "C3"
                case IntInstruction(): inst_hex = f"CD {self._get_value(instruction.imm8):02X}"
                case NopInstruction(): inst_hex = "90"
                
                case DataDeclarationInstruction():
                    inst_hex = self._encode_data(instruction.directive, instruction.value)
                case _: inst_hex = "90"

            if inst_hex:
                final_hex = inst_hex.strip().upper()
                code_lines.append(final_hex)
                self.current_address += len(final_hex.replace(" ", "")) // 2

        return "\n".join(code_lines)

    # --- Ayudantes ---
    def _encode_data(self, directive, value_str):
        try: val = int(value_str)
        except: val = 0
        if directive == 'dd': return f"{(val & 0xFF):02X} {(val >> 8) & 0xFF:02X} {(val >> 16) & 0xFF:02X} {(val >> 24) & 0xFF:02X}"
        elif directive == 'dw': return f"{(val & 0xFF):02X} {(val >> 8) & 0xFF:02X}"
        elif directive == 'db': return f"{val & 0xFF:02X}"
        return ""

    def _handle_jump(self, opcode, label):
        self._add_ref(label)
        target = self.symbol_table.get_address(label) if self.symbol_table else 0
        offset = target - (self.current_address + 2)
        if offset < 0: offset = (offset + 256) & 0xFF
        return f"{opcode} {offset:02X}"

    def _encode_mem_op(self, opcode, reg_expr, mem_expr):
        self._add_ref(mem_expr.address.name)
        reg_val = self._get_reg_value(reg_expr)
        modrm = (reg_val << 3) | 5
        addr = self.symbol_table.get_address(mem_expr.address.name) if self.symbol_table else 0
        return f"{opcode} {modrm:02X} {(addr & 0xFF):02X} {(addr >> 8) & 0xFF:02X} {(addr >> 16) & 0xFF:02X} {(addr >> 24) & 0xFF:02X}"

    def _encode_reg_reg(self, dest, src):
        return f"{0xC0 | (self._get_reg_value(src) << 3) | self._get_reg_value(dest):02X}"

    def _get_reg_value(self, expr):
        if isinstance(expr, IdentifierExpression): return REGISTERS.get(expr.name.lower(), 0)
        return 0

    def _add_ref(self, label):
        if hasattr(self.referenceTable, 'add_usage'): self.referenceTable.add_usage(label, self.current_address)
    
    def _get_value(self, expr): return expr.value if isinstance(expr, IntegerExpression) else 0