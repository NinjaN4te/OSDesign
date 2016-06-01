# ----------------------------------------------------------------------- #
# OPCODES
# ----------------------------------------------------------------------- #
# keep a table to convert assembly code into opcodes + operands, and vice versa


# LIBRARIES
# ----------------------------------------- #


# user libraries/scripts
import constants as c


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #


# OPCODES TABLE
# ----------------------------------------------------------------------- #

# StoreInstructionToDisk
# called from LoadProcessesIntoDiskAsInstruction() from the ProcessLoader module.
#   this takes as an argument a single line of an instruction from that function
#   and then stores it as machine code 'to disk'
def StoreInstructionToDisk(instr, disk):
  getattr(COMMAND, instr[reg['PC']][1])(reg,instr[reg['PC']])
  print(instr)






