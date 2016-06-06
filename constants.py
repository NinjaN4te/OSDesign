# CONSTANTS
import numpy as np

# PATHS
INSTRUCTIONSETPATH = './InstructionSet'

# Instruction Set list index positions for the various elements
INSTRSETMC1 = 2
INSTRSETMC2 = 3
INSTRSETMC3 = 4
INSTRSETMNEMONIC = 5

# control line/pins
RST = 0 # perform hard reset
MWR = 1 # write to lcd unit
CLK = 2 # clock register (machine cycles)
WR  = 3 # write to memory
RD  = 4 # read from memory
CS  = 5 # chip select

# pin state
LO = 0
HI = 1


# another table to convert a sequence of bits into either
#   the destination/source registers, ALU operation, condition flags, etc
DESTINATION = {
  '[0 0 0]': 'B',
  '[0 0 1]': 'C',
  '[0 1 0]': 'D',
  '[0 1 1]': 'E',
  '[1 0 0]': 'H',
  '[1 0 1]': 'L',
  '[1 1 0]': '(HL)',
  '[1 1 1]': 'A'
}


# CPU/MODULES/OTHER
# modules
mA    = 'MODULE A'
mACT  = 'MODULE ACT'
mCU   = 'MODULE CU'
mCTRL = 'MODULE CTRL'
mFLAGS= 'MODULE FLAGS'
mRAM  = 'MODULE RAM'
mTMP  = 'MODULE TMP'

# main memory
mMM   = 'MAIN MEMORY'

# DISK
# the word size of the cpu architecture
WORD      = 8   # 8 bits
DWORD     = 16  # two WORDs are 16 bits
# the disk will have a size of 512 kilobytes, the size of super mario bros 2
DISKSIZE  = 512*1000


# INSTRUCTION DECODER
# instructions have the form:
#   [LABEL] mnemonic [ARG1, ARG2, ...]
LABEL     = 0
MNEMONIC  = 1
ARG1      = 2
ARG2      = 3
# placeholder bits for register, destination, condition, and alu operation addresses in the decoder.
#   the decoder uses these placeholder bits to mask over the argument to find a match
PLACEHOLDERBIT = -1
R   = PLACEHOLDERBIT
D   = PLACEHOLDERBIT
F   = PLACEHOLDERBIT  # 2 bytes: condition, 1 byte: F flags
ALU = PLACEHOLDERBIT
NR3 = PLACEHOLDERBIT  # n >> 3
n   = PLACEHOLDERBIT  # literal value n
ADDRESS = 0
IMMEDIATE = 1
DISPLACEMENT = 2

# flag registers
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
Z = 7
N = 6
H = 5
C = 4

AFFC = -2 # the default input value, indicates that the flag is affected by the operation
UNAF = -1 # specifies that the corresponding flag is not affected by the operation

