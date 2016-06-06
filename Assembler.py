# ----------------------------------------------------------------------- #
# ASSEMBLER
# ----------------------------------------------------------------------- #
# a simple assembler for converting the example programs in processes into machine code
#   store these files in processes/machine_code


# LIBRARIES
# ----------------------------------------- #
import io
import numpy as np
import re

# user libraries/scripts
import constants as c


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #


# ASSEMBLER CLASS
# ----------------------------------------------------------------------- #
class Assembler(object):
  def __init__(self):
    self.optab = OpTable()



  def Assemble(self):
    # file names/paths and memory buffer object
    # -------------------------- #
    filename = 'eg1'
    processesPath = './processes/'
    programsPath = './programs/'


    # HELPER VARIABLES/FUNCTIONS
    # -------------------------- #
    # define some regex expressions to remove the superfluous stuff
    # strip all comments, note that the comments begin with a ';' semicolon
    dcomment  = '([\s]+;[\w\W\s]+)$'
    # split instructions delimited by white spaces and commas
    delim   = '[\s,]+'
    # convert all numbers to ints, base 10, ie: decimals
    dNum = re.compile('''^(
                            [0-9]+          # starts with one or more 0-9s,
                            [0-9a-fA-F]*    # then contains zero or more 0-9a-fA-F,
                          )                 # and
                          (                 # ...
                            H|              # ends with an H (ie: hex),
                            B|              # or ends with a B (ie: binary),
                            (?<![a-fA-F])$  # or does NOT end in a-fA-F (ie: decimal)
                          )$''', re.VERBOSE)
    # function call within the assembling function, converts numbers to decimal base
    def convertToDecimal(matchobj, arg):
      if(matchobj == None):
        # if no match, then return back original argument
        return arg
      # otherwise, convert different base numeral to decimal
      if(matchobj.group(2)=='H'):
        # Hexadecimal
        return int(matchobj.group(1), 16)
      elif(matchobj.group(2)=='B'):
        # Binary
        return int(matchobj.group(1), 2)
      else:
        # Decimal
        return int(matchobj.group(1))

    
    # ASSEMBLE
    # -------------------------- #
    # length of the program, obtain during first pass of assembler
    programlength = 100
    # position of current index
    pos = 0
    # store assembled bytes in this numpy array, this is also the output
    assembledCode = np.zeros(programlength)
    # read in file as process; load in instructions
    with open(processesPath + filename) as f:
      for line in f:             # repeat for every line in the file,
        instr = [                   #   note that every line is only one instruction in my examples
          # convert hex and binary to decimal
          (lambda match = dNum.fullmatch(args):
                convertToDecimal(match, args))()
          # split labels from mnemonics from operands
          for args in re.split( delim,
            # remove comments
            re.sub( dcomment, '', line.rstrip('\n') )
          )
        ]
        # lookup opcodes in OPTAB, store translated machine code into the output
        opcode = getattr(self.optab, instr[ c.MNEMONIC ])(instr)
        assembledCode[pos:pos+opcode.size] = opcode
        pos += opcode.size
    # save the numpy array containing the assembled code to the file
    np.save(programsPath + filename, assembledCode[0:pos])



# OPCODES TABLE
# ----------------------------------------------------------------------- #
# table lookup for opcodes

class OpTable(object):
  def __init__(self):
    pass
  # LOAD COMMANDS
  def LD(self, instr):
  # 1. LD ( r1 , n )
  #       desc: put 8bit value n into register r1
    # OpCodes come in the form XY and range from 00 to FF
    #X, Y = 0, 0
    r1 = instr[ c.ARG1 ]
    r2 = instr[ c.ARG2 ]
    def switcher(arg):
      d = {
        'B': int('06', 16),
        'C': int('0E', 16),
        'D': int('16', 16), 
        'E': int('1E', 16),
        'H': int('26', 16),
        'L': int('2E', 16)
      }
      return d.get(arg, 'ERROR')
    return np.array([ switcher(r1), r2 ])

  # ARITHMETIC ALU OPERATIONS
  # 1. ADD A,n
  #   cycles: 4
  #   desc: Add n to register A.
  #   use with: n = A,B,C,D,E,H,L,(HL),#
  def ADD(self, instr):
    A = instr[ c.ARG1 ]
    n = instr[ c.ARG2 ]
    # n is a register
    def switcher(arg):
      d = {
        'A': int('87', 16),
        'B': int('80', 16),
        'C': int('81', 16),
        'D': int('82', 16),
        'E': int('83', 16),
        'H': int('84', 16),
        'L': int('85', 16)
      }
      return d.get(arg, 'ERROR')
    return np.array([ switcher(n) ])
