# CONSTANTS
import numpy as np

# table to convert index of the opcode into a human-readable string form.
#   use to pass from the Decoder class into the ControllerSequence class to execute
OPCODENAME = {    # {{{2
  0:'NOP',
  1:'LD (N),SP',
  2:'LD R,N',
  3:'ADD HL,R',
  4:'LD (R),A',
  5:'LD A,(R)',
  6:'INC R',
  7:'DEC R',
  8:'INC D',
  9:'DEC D',
  10:'LD D,N',
  11:'RdCA',
  12:'RdA',
  13:'STOP',
  14:'JR N',
  15:'JR F,N',
  16:'LDI (HL),A',
  17:'LDI A,(HL)',
  18:'LDD (HL),A',
  19:'LDD A,(HL)',
  20:'DAA',
  21:'CPL',
  22:'SCF',
  23:'CCE',
  24:'LD D,D',
  25:'HALT',
  26:'ALU A,D',
  27:'ALU A,N',
  28:'POP R',
  29:'PUSH R',
  30:'RST N',
  31:'RET F',
  32:'RET',
  33:'RETI',
  34:'JP F,N',
  35:'JP N',
  36:'CALL F,N',
  37:'CALL N',
  38:'ADD SP,N',
  39:'LD HL,SP+N',
  40:'LD (FF00+N),A',
  41:'LD A,(FF00+N)',
  42:'LD (C),A',
  43:'LD A,(C)',
  44:'LD (N),A',
  45:'LD A,(N)',
  46:'JP HL',
  47:'LD SP,HL',
  48:'DI',
  49:'EI',
  50:'RdC D',
  51:'Rd D',
  52:'SdA D',
  53:'SWAP D',
  54:'SRL D',
  55:'BIT N,D',
  56:'BIT N,D',
  57:'RES N,D',
  58:'SET N,D'
} #}}}2

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

