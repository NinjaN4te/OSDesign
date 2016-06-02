#!/usr/bin/env python

# MAIN file, for OS project
# Scott
# ----------------------------------------------------------------------- #

# LIBRARIES
# ----------------------------------------------------------------------- #
from gmpy2 import xmpz
import re

# user libraries/scripts
import constants as c
import COMMAND
import Disk
import OpCodes
import ProcessLoader


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #
timeslice = 10

# DISK MEMORY
# ----------------------------------------------------------------------- #
# this list will contain the entirety of the physical addresses of the disk memory
disk = Disk.Disk()


# MAIN MEMORY / REAL MEMORY
# ----------------------------------------------------------------------- #


# SAMPLE PROCESS
# ----------------------------------------------------------------------- #


# SAMPLE PROCESSOR
# ----------------------------------------------------------------------- #
#   REGISTERS
reg = {
      # general purpose registers
        'A' : xmpz(0),
        'B' : xmpz(0),
        'C' : xmpz(0),
        'D' : xmpz(0),
        'E' : xmpz(0),
        'H' : xmpz(0),
        'L' : xmpz(0),
      # special registers
        'F' : xmpz(0),  # Flag register
        'SP': 0,  # Stack Pointer register
        #'IC': 0,  # Instruction Counter register, points to next instruction to be executed
        'PC': 0   # Program Counter register, cpu executes instruction at this location
}


# PROCESS LOADER
# ----------------------------------------------------------------------- #
# load the sample process files located in './processes' 'into disk'
ProcessLoader.LoadProcessesIntoDiskAsInstruction(disk)

# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #



# CONVENIENCE FUNCTIONS
# ----------------------------------------------------------------------- #
def printRegisters():
  print(
    # general registers
    'A: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['A'])) + '\n' + 
    'B: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['B'])) + '\n' + 
    'C: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['C'])) + '\n' + 
    'D: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['D'])) + '\n' + 
    'E: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['E'])) + '\n' + 
    'H: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['H'])) + '\n' + 
    'L: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['L'])) + '\n'
  )
  # flag register
  print('   ZNHC0000')
  print('F: {:0>8b}'.format(int(reg['F'])))


# run loop
while(reg['PC'] < disk.getNumBytes()):
  try:
    if(OpCodes.getNextOp() == True):
      # fetch new instruction
      #print('{:02X}'.format(disk.GetByteAt(reg['PC']*c.WORD)))
      instr = OpCodes.parseByte(disk.GetByteAt(reg['PC']*c.WORD))
    else:
      # if not, then append operands to our instruction
      instr.append(OpCodes.parseByte(disk.GetByteAt(reg['PC']*c.WORD)))
    # check again to see if we can execute in same cycle
    if(OpCodes.getNextOp() == True):
      # execute instruction if we have the whole instruction in memory
      instr = getattr(COMMAND, instr[1])(reg,instr)
  except AttributeError:
    # if failed, then throw error
    print('\n/!\\/!\\/!\\ ERROR /!\\/!\\/!\\')
    print('Error executing instruction: ' + str(instr[reg['PC']]))
    print('PC at ' + str(reg['PC']))
    print('')
    raise

  # increment Program Counter
  reg['PC'] += 1



#print(instr)
print(reg)
printRegisters()
