# ----------------------------------------------------------------------- #
# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #
# decodes the binary instruction
# keep a table to convert assembly code into opcodes + operands, and vice versa


# LIBRARIES
# ----------------------------------------- #
import numpy as np


# user libraries/scripts
import constants as c
from constants import R, D, F, ALU, NR3, n


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# DECODER CLASS
# ----------------------------------------------------------------------- #
class Decoder(object):    #{{{2
  def __init__(self, cu):
    # hold a reference to the CU (Control Unit) that created this Decoder module class
    self.cu = cu
    # create the opcode table object for the decoder
    self.optab = OpCodeTable()
    # the Controller Sequencer class will receive from the instruction Decoder class
    #   the index of the opcode to execute and the byte of data (usually the instruction)
    #   itself to use. Use this table to determine which command to execute within
    #   the class
    self.opcodeDict = {   # {{{2
      'NOP'       : self.cu.ctrlSeq.nothing,
      'LD (N),SP' : self.cu.ctrlSeq.nothing,
      'LD R,N'    : self.cu.ctrlSeq.nothing,
      'ADD HL,R'  : self.cu.ctrlSeq.nothing,
      'LD (R),A'  : self.cu.ctrlSeq.nothing,
      'LD A,(R)'  : self.cu.ctrlSeq.nothing,
      'INC R'     : self.cu.ctrlSeq.nothing,
      'DEC R'     : self.cu.ctrlSeq.nothing,
      'INC D'     : self.cu.ctrlSeq.nothing,
      'DEC D'     : self.cu.ctrlSeq.nothing,
      'LD D,N'    : self.cu.ctrlSeq.LDDN,
      'RdCA': self.cu.ctrlSeq.nothing,
      'RdA': self.cu.ctrlSeq.nothing,
      'STOP': self.cu.ctrlSeq.nothing,
      'JR N': self.cu.ctrlSeq.nothing,
      'JR F,N': self.cu.ctrlSeq.nothing,
      'LDI (HL),A': self.cu.ctrlSeq.nothing,
      'LDI A,(HL)': self.cu.ctrlSeq.nothing,
      'LDD (HL),A': self.cu.ctrlSeq.nothing,
      'LDD A,(HL)': self.cu.ctrlSeq.nothing,
      'DAA': self.cu.ctrlSeq.nothing,
      'CPL': self.cu.ctrlSeq.nothing,
      'SCF': self.cu.ctrlSeq.nothing,
      'CCE': self.cu.ctrlSeq.nothing,
      'LD D,D': self.cu.ctrlSeq.nothing,
      'HALT': self.cu.ctrlSeq.nothing,
      'ALU A,D': self.cu.ctrlSeq.nothing,
      'ALU A,N': self.cu.ctrlSeq.nothing,
      'POP R': self.cu.ctrlSeq.nothing,
      'PUSH R': self.cu.ctrlSeq.nothing,
      'RST N': self.cu.ctrlSeq.nothing,
      'RET F': self.cu.ctrlSeq.nothing,
      'RET': self.cu.ctrlSeq.nothing,
      'RETI': self.cu.ctrlSeq.nothing,
      'JP F,N': self.cu.ctrlSeq.nothing,
      'JP N': self.cu.ctrlSeq.nothing,
      'CALL F,N': self.cu.ctrlSeq.nothing,
      'CALL N': self.cu.ctrlSeq.nothing,
      'ADD SP,N': self.cu.ctrlSeq.nothing,
      'LD HL,SP+N': self.cu.ctrlSeq.nothing,
      'LD (FF00+N),A': self.cu.ctrlSeq.nothing,
      'LD A,(FF00+N)': self.cu.ctrlSeq.nothing,
      'LD (C),A': self.cu.ctrlSeq.nothing,
      'LD A,(C)': self.cu.ctrlSeq.nothing,
      'LD (N),A': self.cu.ctrlSeq.nothing,
      'LD A,(N)': self.cu.ctrlSeq.nothing,
      'JP HL': self.cu.ctrlSeq.nothing,
      'LD SP,HL': self.cu.ctrlSeq.nothing,
      'DI': self.cu.ctrlSeq.nothing,
      'EI': self.cu.ctrlSeq.nothing,
      'RdC D': self.cu.ctrlSeq.nothing,
      'Rd D': self.cu.ctrlSeq.nothing,
      'SdA D': self.cu.ctrlSeq.nothing,
      'SWAP D': self.cu.ctrlSeq.nothing,
      'SRL D': self.cu.ctrlSeq.nothing,
      'BIT N,D': self.cu.ctrlSeq.nothing,
      'BIT N,D': self.cu.ctrlSeq.nothing,
      'RES N,D': self.cu.ctrlSeq.nothing,
      'SET N,D':self.cu.ctrlSeq.nothing
    }   #}}}2

  # parse binary machine code into opcodes and operands
  # ----------------------------------------------------------------------- #
  def parseByte(self, byte):
    self.cu.instr = c.OPCODENAME[self.optab.lookupOPCODE(byte)]
  #}}}2

  def executeSeq(self, opcode, byte):
    self.sequenceDict[opcode](byte)

  # OPCODE TABLE LOOKUP CLASS
  # ----------------------------------------------------------------------- #
  # returns a numpy boolean index that uses the bitwise equivalence function
  #   implemented in BinaryFunctions.py, but additionally allows register,
  #   destination, ALU operations, or condition placeholder representatives/bits
  #   that will be defined as below:
  #     (referenced from goldencrystal.free.fr/GBZ80Opcodes.pdf)
  #
  #   REGISTER:                 CONDITION:
  #         |  R |  R |  R              Mnemonic|  F
  #   ------+----+----+----     -----------+----+----
  #     BC  |  0 | 00 | 00       Not Zero  | NZ | 00
  #     DE  |  1 | 01 | 01       Zero      |  Z | 01
  #     HL  |  / | 10 | 10       Not Carry | NC | 10
  #     SP  |  / | 11 | //       Carry     |  C | 22
  #     AF  |  / | // | 11
  #
  #   DESTINATION:              OPERATION:
  #    Rgstr|  D                        ALU
  #   ------+-----              ------+-----
  #      B  | 000                ADD  | 000
  #      C  | 001                ADC  | 001
  #      D  | 010                SUB  | 010
  #      E  | 011                SBC  | 011
  #      H  | 100                AND  | 100
  #      L  | 101                XOR  | 101
  #    (HL) | 110                OR   | 110
  #      A  | 111                CP   | 111

# create the OpCode Table class
class OpCodeTable(object):
  def __init__(self):
    # create the actual OPTAB as an array mask to utilize numpy's vectorization capabilities
    # OPTAB {{{2
    self.opcodeTable = np.array ([
      [ # NOP
        0 , 0 , 0 , 0 , 0 , 0 , 0 , 0],
      [ # LD (N), SP
        0 , 0 , 0 , 0 , 1 , 0 , 0 , 0],
      [ # LD R,N
        0 , 0 , R , R , 0 , 0 , 0 , 1],
      [ # ADD HL,R
        0 , 0 , R , R , 1 , 0 , 0 , 1],
      [ # LD (R),A
        0 , 0 , 0 , R , 0 , 0 , 1 , 0],
      [ # LD A,(R)
        0 , 0 , 0 , R , 1 , 0 , 1 , 0],
      [ # INC R
        0 , 0 , R , R , 0 , 0 , 1 , 1],
      [ # DEC R
        0 , 0 , R , R , 1 , 0 , 1 , 1],
      [ # INC D
        0 , 0 , D , D , D , 1 , 0 , 0],
      [ # DEC D
        0 , 0 , D , D , D , 1 , 0 , 1],
      [ # LD D,N
        0 , 0 , D , D , D , 1 , 1 , 0],
      [ # RdCA
        0 , 0 , 0 , 0 , D , 1 , 1 , 1],
      [ # RdA
        0 , 0 , 0 , 1 , D , 1 , 1 , 1],
      [ # STOP
        0 , 0 , 0 , 1 , 0 , 0 , 0 , 0],
      [ # JR N
        0 , 0 , 0 , 1 , 1 , 0 , 0 , 0],
      [ # JR F,N
        0 , 0 , 1 , F , F , 0 , 0 , 0],
      [ # LDI (HL),A
        0 , 0 , 1 , 0 , 0 , 0 , 1 , 0],
      [ # LDI A,(HL)
        0 , 0 , 1 , 0 , 1 , 0 , 1 , 0],
      [ # LDD (HL),A
        0 , 0 , 1 , 1 , 0 , 0 , 1 , 0],
      [ # LDD A,(HL)
        0 , 0 , 1 , 1 , 1 , 0 , 1 , 0],
      [ # DAA
        0 , 0 , 1 , 0 , 0 , 1 , 1 , 1],
      [ # CPL
        0 , 0 , 1 , 0 , 1 , 1 , 1 , 1],
      [ # SCF
        0 , 0 , 1 , 1 , 0 , 1 , 1 , 1],
      [ # CCF
        0 , 0 , 1 , 1 , 1 , 1 , 1 , 1],
      # ----------------------------- #
      [ # LD D,D
        0 , 1 , D , D , D , D , D , D],
      [ # HALT
        0 , 1 , 1 , 1 , 0 , 1 , 1 , 0],
      [ # ALU A,D
        1 , 0 ,ALU,ALU,ALU, D , D , D],
      [ # ALU A,N
        1 , 1 ,ALU,ALU,ALU, 1 , 1 , 0],
      [ # POP R
        1 , 1 , R , R , 0 , 0 , 0 , 1],
      [ # PUSH R
        1 , 1 , R , R , 0 , 1 , 0 , 1],
      [ # RST N
        1 , 1 ,NR3,NR3,NR3, 1 , 1 , 1],
      # ----------------------------- #
      [ # RET F
        1 , 1 , 0 , F , F , 0 , 0 , 0],
      [ # RET
        1 , 1 , 0 , 0 , 1 , 0 , 0 , 1],
      [ # RETI
        1 , 1 , 0 , 1 , 1 , 0 , 0 , 1],
      [ # JP F,N
        1 , 1 , 0 , F , F , 0 , 1 , 0],
      [ # JP N
        1 , 1 , 0 , 0 , 0 , 0 , 1 , 1],
      [ # CALL F,N
        1 , 1 , 0 , F , F , 1 , 0 , 0],
      [ # CALL N
        1 , 1 , 0 , 0 , 1 , 1 , 0 , 1],
      [ # ADD SP,N
        1 , 1 , 1 , 0 , 1 , 0 , 0 , 0],
      [ # LD HL,SP+N
        1 , 1 , 1 , 1 , 1 , 0 , 0 , 0],
      [ # LD (FF00+N),A
        1 , 1 , 1 , 0 , 0 , 0 , 0 , 0],
      [ # LD A,(FF00+N)
        1 , 1 , 1 , 1 , 0 , 0 , 0 , 0],
      [ # LD (C),A
        1 , 1 , 1 , 0 , 0 , 0 , 1 , 0],
      [ # LD A,(C)
        1 , 1 , 1 , 1 , 0 , 0 , 1 , 0],
      [ # LD (N),A
        1 , 1 , 1 , 0 , 1 , 0 , 1 , 0],
      [ # LD A,(N)
        1 , 1 , 1 , 1 , 1 , 0 , 1 , 0],
      [ # JP HL
        1 , 1 , 1 , 0 , 1 , 0 , 0 , 1],
      [ # LD SP,HL
        1 , 1 , 1 , 1 , 1 , 0 , 0 , 1],
      [ # DI
        1 , 1 , 1 , 1 , 0 , 0 , 1 , 1],
      [ # EI
        1 , 1 , 1 , 1 , 1 , 0 , 1 , 1],
      # ----------------------------- #
      [ # RdC D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # Rd D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # SdA D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # SWAP D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # SRL D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # BIT N,D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # RES N,D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1],
      [ # SET N,D
        1 , 1 , 0 , 0 , 1 , 0 , 1 , 1]
    ])
    #}}}2
  #}}}1
  # function within the OpCodeTables object,
  #   accepts an instruction as a parameter that we will then
  #   lookup the opcode for in the table
  def lookupOPCODE(self, instr):
    # first mask opcode table over the instruction
    mask = np.logical_or(self.opcodeTable == instr, self.opcodeTable  == c.PLACEHOLDERBIT)
    # find the exact match, ie: all 8 bits match
    match = mask.sum(axis=1)>7
    # find the index of the match, that is the opcode we return
    opcode = np.flatnonzero(match)[0]
    # return the opcode
    return opcode


