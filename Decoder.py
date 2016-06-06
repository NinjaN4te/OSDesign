# ----------------------------------------------------------------------- #
# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #
# decodes the binary instruction
# keep a table to convert assembly code into opcodes + operands, and vice versa


# LIBRARIES
# ----------------------------------------- #
import numpy as np
import re


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

  # parse binary machine code into opcodes and operands
  # ----------------------------------------------------------------------- #
  def parseByte(self, byte):
    #self.cu.instr = self.optab.instrSet[0][c.INSTRSETMNEMONIC]
    self.cu.instr = byte
    self.cu.nextOp = self.optab.instrSet[0][c.INSTRSETMC2]
  #}}}2

  def executeSeq(self, opcode, byte):
    self.opcodeDict[opcode](byte)

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
    # load the instruction set from file
    # creates the actual OPTAB to use as an array mask to utilize numpy's vectorization capabilities
    # self.instrset, self.opcodeTable are created and initialized here!
    self.LoadInstructionSet(c.INSTRUCTIONSETPATH)
  # function within the OpCodeTables object,
  #   accepts an instruction as a parameter that we will then
  #   lookup the opcode for in the table
  def lookupOPCODE(self, instr):
    # first mask opcode table over the instruction
    #mask = np.logical_or(self.opcodeTable == instr, self.opcodeTable  == c.PLACEHOLDERBIT)
    # find the exact match, ie: all 8 bits match
    #match = mask.sum(axis=1)>7
    # find the index of the match, that is the opcode we return
    #opcode = np.flatnonzero(match)[0]
    # return the opcode
    #return opcode
    pass


  # load the instruction set of the cpu from file
  def LoadInstructionSet(self, path):
    # define regex expressions to remove unwanted stuff
    # strip all comments, all comments begin with a '#' hashtag
    dcomment = '([\s]+;[\w\W\s]+)$'
    # open the file
    with open(c.INSTRUCTIONSETPATH) as f:
      self.instrSet = [
        # split each line on white spaces
        re.split( '\s+', 
          # remove all comments, comments begin with a '#'
          re.sub( dcomment, '', line.rstrip('\n')),
        # don't split the mnemonic string
        maxsplit=5 )
      # loop over the file and grab the line if it's not empty, the first line, or a comment line
      for line in f if not line.startswith(('opcode', ' ', '\n', ';'))  ]

    # now make the opcode mask table
    # create a new generator function that will return the bits in the string,
    #   taking into consideration the possible placeholder bits like D, L, S, etc.
    #   these are defined in the constants.py file
    def bits():
      i = 0
      # iterate over the instruction set and grab the first element, which is the opcode, from
      #   each line
      for line in self.instrSet:
        # opcode is the first element in the line, as can be seen in the InstructionSet file
        opcode = line[0]
        # now iterate over each bit in the opcode
        for bit in opcode:
          # check if the bit is a placeholder bit and deal with it appropriately
          try:
            # 0 or 1
            yield int(bit)
          except ValueError:
            # a placeholder bit, ie: it's a character, eg: D, L, S, etc
            yield c.PLACEHOLDERBIT

    self.opcodeTable = np.fromiter(bits(), np.uint8)
    self.opcodeTable.shape = (len(self.instrSet), 8)

    return True

