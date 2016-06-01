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


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #
timeslice = 10

# DISK MEMORY
# ----------------------------------------------------------------------- #


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
# load example processes 'into disk'
#   simulate processes stored in disk; assign disk addresses and etc

# regex expressions to remove the superfluous stuff
# strip all comments, note that the comments begin with a ';' semicolon
dcomment  = '([\s]+;[\w\W\s]+)$'
# split instructions delimited by white spaces and commas
delim   = '[\s,]+'
# convert all pure numbers to base 10 (decimal) as a xmpz object from gmpy2 library
dNum = re.compile('''^(
                        [0-9]+          # starts with one or more 0-9s,
                        [0-9a-fA-F]*    # then contains zero or more 0-9a-fA-F,
                      )                 # and
                      (                 # ...
                        H|              # ends with an H (ie: hex),
                        B|              # or ends with a B (ie: binary),
                        (?<![a-fA-F])$  # or does NOT end in a-fA-F (ie: decimal)
                      )$''', re.VERBOSE)

# function call within the loading function, converts numbers to decimal base
def convertToDecimal(matchobj, arg):
  if(matchobj == None):
    # if no match, then return back original argument
    return arg
  # otherwise, convert different base numeral to decimal
  if(matchobj.group(2)=='H'):
    # Hexadecimal
    return xmpz(int(matchobj.group(1), 16))
  elif(matchobj.group(2)=='B'):
    # Binary
    return xmpz(int(matchobj.group(1), 2))
  else:
    # Decimal
    return xmpz(int(matchobj.group(1)))

# read in file as process; load in instructions
with open('./processes/eg1') as file: instr = (
            [[
            # convert hex and binary to decimal
            (lambda match = dNum.fullmatch(args):
                  convertToDecimal(match, args))()
            # split labels from mnemonics from operands
            for args in re.split( delim,
                # remove comments
                re.sub( dcomment, '', line.rstrip('\n') )
            )]
          for line in file] )


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
    'L: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(reg['L'])) + '\n' + 
                                                              '\n'
  )
  # flag register
  print('   ZNHC0000')
  print('F: {:0>8b}'.format(int(reg['F'])))

# run loop
while(reg['PC'] < len(instr)):
  try:
    # decode instruction and execute
    getattr(COMMAND, instr[reg['PC']][1])(reg,instr[reg['PC']])
  except AttributeError:
    # if failed, then throw error
    print('Error executing instruction: ' + str(instr[reg['PC']]))
    print('PC at ' + str(reg['PC']))
    print('')
    raise

  # increment Program Counter
  reg['PC'] += 1



#print(instr)
print(reg)
printRegisters()
