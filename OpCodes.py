# ----------------------------------------------------------------------- #
# OPCODES
# ----------------------------------------------------------------------- #
# keep a table to convert assembly code into opcodes + operands, and vice versa


# LIBRARIES
# ----------------------------------------- #
import numpy as np


# user libraries/scripts
import constants as c


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #
# nextOp is true when the parser has finished parsing the whole instruction.
#   note that instructions can be from 1-4 bytes, though most are just 1.
#   if nextOp is True, then the parser will parse the next byte as an OpCode
#   if nextOp is False, then the parser will parse the next byte as a value
nextOp = True
# number of operands that are left for the operation.
#   nextOp becomes True when operands hits 0
#   when setting it in the parser, set it to (instruction byte size)-1
#     ie: if the instruction only occupies 1 byte, there are no operands
operands = 0


# OPCODES TABLE
# ----------------------------------------------------------------------- #
  
# LOAD COMMANDS
def LD(instr):
# 1. LD ( r1 , n )
#       desc: put 8bit value n into register r1
  # OpCodes come in the form XY and range from 00 to FF
  #X, Y = 0, 0
  bytelist = []
  r1 = instr[ c.ARG1 ]
  r2 = instr[ c.ARG2 ]
  def switcher(arg):
    d = {
      'B': np.unpackbits(np.array([int('06', 16)],dtype=np.uint8)).astype(np.byte),
      'C': np.unpackbits(np.array([int('0E', 16)],dtype=np.uint8)).astype(np.byte),
      'D': np.unpackbits(np.array([int('16', 16)],dtype=np.uint8)).astype(np.byte), 
      'E': np.unpackbits(np.array([int('1E', 16)],dtype=np.uint8)).astype(np.byte),
      'H': np.unpackbits(np.array([int('26', 16)],dtype=np.uint8)).astype(np.byte),
      'L': np.unpackbits(np.array([int('2E', 16)],dtype=np.uint8)).astype(np.byte),
    }
    return d.get(arg, 'ERROR')
  bytelist.append(switcher(r1))
  bytelist.append(np.unpackbits(np.array([int(r2)],dtype=np.uint8)).astype(np.byte))
  return bytelist

# ARITHMETIC ALU OPERATIONS
# 1. ADD A,n
#   cycles: 4
#   desc: Add n to register A.
#   use with: n = A,B,C,D,E,H,L,(HL),#
def ADD(instr):
  bytelist = []
  A = instr[ c.ARG1 ]
  n = instr[ c.ARG2 ]
  # n is a register
  def switcher(arg):
    d = {
      'A': np.unpackbits(np.array([int('87', 16)],dtype=np.uint8)).astype(np.byte),
      'B': np.unpackbits(np.array([int('80', 16)],dtype=np.uint8)).astype(np.byte),
      'C': np.unpackbits(np.array([int('81', 16)],dtype=np.uint8)).astype(np.byte),
      'D': np.unpackbits(np.array([int('82', 16)],dtype=np.uint8)).astype(np.byte),
      'E': np.unpackbits(np.array([int('83', 16)],dtype=np.uint8)).astype(np.byte),
      'H': np.unpackbits(np.array([int('84', 16)],dtype=np.uint8)).astype(np.byte),
      'L': np.unpackbits(np.array([int('85', 16)],dtype=np.uint8)).astype(np.byte)
    }
    return d.get(arg, 'ERROR')
  bytelist.append(switcher(n))
  return bytelist


# parse opcodes and operands into assembly code
# ----------------------------------------------------------------------- #
def parseByte(byte):
  global nextOp
  global operands
  # first check if we will be parsing a new instruction or completing an old one
  if(nextOp==True):
    # parse as OpCode
    #   the first element is the number of bytes the instruction occupies on the disk,
    #     and the second element is the list to return to the caller to use with COMMAND
    def switcher(arg):
      op = {
      # LOAD COMMANDS
      # 1. LD r1,n
      #     2 bytes, 8 cycles
        '06': [2, ['', 'LD', 'B']], #   B,n
        '0E': [2, ['', 'LD', 'C']], #   C,n
        '16': [2, ['', 'LD', 'D']], #   D,n
        '1E': [2, ['', 'LD', 'E']], #   E,n
        '26': [2, ['', 'LD', 'H']], #   H,n
        '2E': [2, ['', 'LD', 'L']], #   L,n


      # ARITHEMTIC ALU OPERATIONS
      # 1. ADD A,n
      #     1 byte, 4 cycles
        '87': [1, ['', 'ADD', 'A', 'A']], #   A,A
        '80': [1, ['', 'ADD', 'A', 'B']], #   A,B
        '81': [1, ['', 'ADD', 'A', 'C']], #   A,C
        '82': [1, ['', 'ADD', 'A', 'D']], #   A,D
        '83': [1, ['', 'ADD', 'A', 'E']], #   A,E
        '84': [1, ['', 'ADD', 'A', 'H']], #   A,H
        '85': [1, ['', 'ADD', 'A', 'L']]  #   A,L
        
      }
      return op.get(arg, [999, 'ERROR'])
    byte = '{:02X}'.format(np.packbits(byte)[0])
    ret = switcher(byte)
    operands = ret[0] - 1   # set the number of operands left
    # check if any operands left
    if(operands <= 0): nextOp = True
    # if so, parse next byte as a value
    else: nextOp = False

    return ret[1]           # return the second element, which is the assembly code
  else:
    # parse as value
    # decrement operands as we parse them
    operands -= 1
    # if we don't have any operands left, then set nextOp to true,
    #   as the current instruction has been fully read
    if(operands <= 0):
      nextOp = True
    return byte


def getNextOp():
  return nextOp

def getOperands():
  return operands



