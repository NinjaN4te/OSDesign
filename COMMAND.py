# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #
import constants as c
from gmpy2 import xmpz

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
    if(res == 0):
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
    if(res[8] == 1):
      # set carry flag if the (n+1)th bit is set after an n-bit operation
      C = 1     # carry flag
    else:
      C = 0
  flags[ c.Z ] = Z
  flags[ c.N ] = N
  flags[ c.H ] = H
  flags[ c.C ] = C

# BOOLEAN MASK OPERATIONS
# boolean AND
def maskAND(b1, b2):
  ret = xmpz(0)
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] == 1 and b2[p] == 1):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

def maskOR(b1, b2):
  ret = xmpz(0)
  for p in range(0, 8):
    if(b1[p] == 1 or b2[p] == 1):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

def maskXOR(b1, b2):
  ret = xmpz(0)
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] != b2[p]):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

# bitwise operations
def leftShift(b1, n, trunc=True):
  stop = 0
  # there is no need to iterate through all the bits, only 8-n bits
  if(trunc == True):
    # get the lower value
    if(b1.bit_length()+n < 8-n):
      stop = b1.bit_length()+n
    else:
      stop = 8-n
  else:
    # don't truncate
    stop = b1.bit_length()+n
  for p in reversed(range(n,stop)):
    # shift to left by n
    b1[p] = b1[p-n]
  # set all lower bits under n to 0
  b1[:n] = 0

  


# LOAD COMMANDS
# 1. LD r1, r2
#       desc: put value of r2 into r1
def LD(reg, instr):
  r1 = instr[ c.ARG1 ]
  r2 = instr[ c.ARG2 ]
  if(r1 in reg):
    reg[r1] = r2

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
    updateFlags(reg['F'], reg[ A ], n)
  except TypeError:
    # n is a register
    carry = reg[ n ]                    # store the operand as the carry
    while(carry != 0):                  # loop until carry is zero, ie: addition complete!
      tSum = maskXOR(reg[ A ], carry)   # new temporary sum w/out carry is XOR between reg and carry
      carry = maskAND(reg[ A ], carry)  # get new carry between the previous sum and carry
      leftShift(carry, 1, trunc=False)  #   left shift by one to position over next digit
      reg[ A ] = tSum                   # store new temporary sum in register
    updateFlags(reg['F'], reg[ A ], reg[ n ])

  # unset any bits higher than the 7th, ie: more than 1 byte
  reg[ A ][8:] = 0
    










