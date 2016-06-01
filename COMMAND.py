# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #
from bitstring import BitArray
import constants as c

# regular integer values are decimal, while hex is appended by H, binary with B
#   note, all numerical values must start with a number from 0-9! hence, 0FFH
# list of current commands:

# UPDATE FLAG REGISTER
def updateF(reg, Z, N, H, C):
  reg['F'][c.Z] = Z
  reg['F'][c.N] = N
  reg['F'][c.H] = H
  reg['F'][c.C] = C

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
  #reg[
  pass
