class Expression:
  def __init__(self):
    self.type = type

class IdentifierExpression(Expression):
  def __init__(self, name: str):
    self.name = name

class IntegerExpression(Expression):
  def __init__(self, value: int):
    self.value = value

class MemoryExpression(Expression):
  def __init__(self, address: Expression):
    self.address = address

class BinaryExpression(Expression):
  def __init__(self, left: Expression, operator: str, right: Expression):
    self.left = left
    self.operator = operator
    self.right = right

class Instruction:
  def __init__(self):
    self.type = type

class MoveInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class AddInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class SubInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class XorInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class AndInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class OrInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class MovzxInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src

class XchgInstruction(Instruction):
  def __init__(self, op1: Expression, op2: Expression):
    self.op1 = op1
    self.op2 = op2

class CmpInstruction(Instruction):
  def __init__(self, op1: Expression, op2: Expression):
    self.op1 = op1
    self.op2 = op2

class TestInstruction(Instruction):
  def __init__(self, op1: Expression, op2: Expression):
    self.op1 = op1
    self.op2 = op2

class LeaInstruction(Instruction):
  def __init__(self, reg: Expression, mem: Expression):
    self.reg = reg
    self.mem = mem

class IncInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class DecInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class MulInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class ImulInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class DivInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class IdivInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class PushInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class PopInstruction(Instruction):
  def __init__(self, op: Expression):
    self.op = op

class IntInstruction(Instruction):
  def __init__(self, imm8: Expression):
    self.imm8 = imm8

class JmpInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JeInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JneInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JleInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JlInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JzInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JnzInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JaInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JaeInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JbInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JbeInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JgInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class JgeInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class CallInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class LoopInstruction(Instruction):
  def __init__(self, label: str):
    self.label = label

class RetInstruction(Instruction):
  def __init__(self):
    pass

class NopInstruction(Instruction):
  def __init__(self):
    pass

class DirectiveInstruction(Instruction):
  def __init__(self, directive: str, operands: str):
    self.directive = directive
    self.operands = operands

class DataDeclarationInstruction(Instruction):
  def __init__(self, label: str, directive: str, value: str):
    self.label = label
    self.directive = directive
    self.value = value

class ImulTwoInstruction(Instruction):
  def __init__(self, dest: Expression, src: Expression):
    self.dest = dest
    self.src = src