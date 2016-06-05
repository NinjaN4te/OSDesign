# Controller Sequencer
# ----------------------------------------------------------------------- #
# executes an assembly instruction decoded by the instruction decoder prior


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/modules
import constants as c
import BinaryFunctions as bf


# CONTROLLER SEQUENCER CLASS
# ----------------------------------------------------------------------- #
class ControllerSequencer(object):
  def __init__(self, cu):
    # hold a reference to the CU (Control Unit) that created this Decoder module class
    self.cu = cu

  # COMMANDS
  # ------------------ #
  # LOAD COMMANDS
  # 10. LD D,N
  # BYTES = ||  0 1 . D D D . 1 1 0   || 8 BIT IMMEDIATE
  # DESCRIPTION: Load 8-bit immediate into a destination register
  def LDDN(self, byte):
    dest = c.DESTINATION[np.array_str(byte[2:5])]
    if(dest in self.cu.cpu.reg):
      self.cu.cpu.reg[dest] = byte

  def nothing(self, byte):
    print('{:} not yet implemented'.format(byte))

# regular integer values are decimal, while hex is appended by H, binary with B
#   note, all numerical values must start with a number from 0-9! hence, 0FFH
# list of current commands:

# UPDATE FLAG REGISTER
# the Flag Register F consists of the following bits:
# 7 6 5 4 3 2 1 0
# Z N H C 0 0 0 0
# ---------------
# Zero Flag (Z):
#   This bit is set when the result of a math operation
#   is zero or two values match when using the CP
#   instruction.
# Subtract Flag (S):
#   This bit is set if a subtraction was performed in the
#   last math instruction.
# Half Carry Flag (H):
#   This bit is set if a carry occurred from the lower
#   nibble in the last math operation (if carry from bit 3).
# Carry Flag (C):
#   This bit is set if a carry occurred from the last
#   math operation (if carry from bit 7) or if
#   register A is the smaller value when executing
#   the CP instruction.
# ARGS:
#   flags : the F register
#   res   : the final value of the register after the operation
#   opr   : the operand, or argument in the instruction
#   ZNHC  : the operation can manually specify whether the flag is 0, 1, or c.UNAF: unaffected
def updateFlags(flags, res, opr, Z=c.AFFC, N=c.AFFC, H=c.AFFC, C=c.AFFC):
  # set flag bits to existing bits if they are unaffected by the operation
  #   otherwise compute new flag values
  # zero flag
  if(Z == c.UNAF): Z = flags[ c.Z ]
  elif(Z == c.AFFC):
    if(np.sum(res, dtype=np.byte, axis=0) == 0):
      # set zero flag if the result is zero
      Z = 1     # zero flag
    else:
      Z = 0

  # subtract flag
  if(N == c.UNAF): N = flags[ c.N ]
  elif(N == c.AFFC):
    N = 1

  # half carry flag
  if(H == c.UNAF): H = flags[ c.H ]
  elif(H == c.AFFC):
    H = 1

  # carry flag
  if(C == c.UNAF): C = flags[ c.C ]
  elif(C == c.AFFC):
    #if(res[8] == 1):
      # set carry flag if the (n+1)th bit is set after an n-bit operation
      #C = 9     # carry flag
    C = 9     # carry flag
    #else:
    #  C = 0
  flags[ c.Z ] = Z
  flags[ c.N ] = N
  flags[ c.H ] = H
  flags[ c.C ] = C



# ARITHMETIC ALU
# 1. ADD A,n
#   cycles: 4
#   desc: Add n to A.
#   use with: n = A,B,C,D,E,H,L,(HL),#
#   Flags affected:
#     Z - set if result is zero
#     N - Reset.
#     H - Set if carry from bit 3.
#     C - Set if carry from bit 7.
def ADD(reg, instr):
  A = instr[ c.ARG1 ]
  n = instr[ c.ARG2 ]
  try:
    # n is a number, '#'
    reg[ A ] += n
    print('ADD not yet implemented')
    raise
    #updateFlags(reg['F'], reg[ A ], n)
  except TypeError:
    # n is a register
    reg[ A ] = np.bitwise_xor(reg[ A ], reg[ n ])
    carry = reg[ n ]                    # store the operand as the carry
    while(np.any(carry)):               # loop until carry is zero, ie: addition complete!
      tSum = np.bitwise_xor(reg[ A ], carry)# new temporary sum w/out carry is XOR between reg and carry
      carry = np.bitwise_and(reg[ A ], carry)  # get new carry between the previous sum and carry
      bf.leftShift(carry, 1)  #   left shift by one to position over next digit
      reg[ A ] = tSum                   # store new temporary sum in register
    updateFlags(reg['F'], reg[ A ], reg[ n ])










