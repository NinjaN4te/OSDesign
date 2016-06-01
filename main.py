#!/usr/bin/env python

# MAIN file, for OS project
# Scott
# ----------------------------------------------------------------------- #

# LIBRARIES
# ----------------------------------------------------------------------- #
import bitstring as bs
from bitstring import *
import re

# user libraries/scripts
import constants as c
import COMMAND


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
      # '>b' denotes big-endian signed 8bit integers
      # general purpose registers
        'A' : bs.pack('>b', 0),
        'B' : bs.pack('>b', 0),
        'C' : bs.pack('>b', 0),
        'D' : bs.pack('>b', 0),
        'E' : bs.pack('>b', 0),
        'H' : bs.pack('>b', 0),
        'L' : bs.pack('>b', 0),
      # special registers
        'F' : bs.pack('>b', 0),  # Flag register
        'SP': 0,  # Stack Pointer register
        #'IC': 0,  # Instruction Counter register, points to next instruction to be executed
        'PC': 0   # Program Counter register, cpu executes instruction at this location
}


# PROCESS LOADER
# ----------------------------------------------------------------------- #
# create an example process, load from file
# strip all comments, note that the comments begin with a ';' semicolon
dcomment  = '([\s]+;[\w\W\s]+)$'
# split instructions delimited by white spaces and commas
delim   = '[\s,]+'
# convert hexadecimal and binary numbers to decimal
dHexBin = re.compile('^([0-9]+[0-9a-fA-F]+)([HB])$')
# function call within the loading function, converts numbers to decimal base
def convertToDecimal(matchobj, arg):
  if(matchobj == None):
    # if no match, then return back original argument
    return arg
  # otherwise, convert different base numeral to decimal
  if(matchobj.group(2)=='H'):
    # Hexadecimal
    try:
      # a cooperative hex number
      return bs.pack('hex:8', matchobj.group(1))
    except bs.CreationError:
      # if the hex number is preceded by a 0, remove it
      return bs.pack('hex:8', matchobj.group(1)[1:])
  elif(matchobj.group(2)=='B'):
    # Binary
    try:
      # a cooperative binary number
      return bs.pack('bin:8', matchobj.group(1))
    except bs.CreationError:
      # if the binary number is less than 8 bits, fill higher
      #   space with leading 0s
      #   (ie: for big-endian use the right-align '>')
      return bs.pack('bin:8', '{:0>8}'.format(matchobj.group(1)))
  else:
    return 'ERROR'

# read in file as process; load in instructions
with open('./processes/eg1') as file: instr = (
            [[
            # convert hex and binary to decimal
            (lambda match = dHexBin.match(args):
                  convertToDecimal(match, args))()
            # split labels from mnemonics from operands
            for args in re.split( delim,
            #re.split( delim,
                # remove comments
                re.sub( dcomment, '', line.rstrip('\n') )
            )]
          for line in file] )


# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #

# run loop
while(reg['PC'] < len(instr)):
  try:
    # decode instruction and execute
    getattr(COMMAND, instr[reg['PC']][1])(reg,instr[reg['PC']])
  except AttributeError:
    # if failed, then throw error
    print("Error executing instruction: " + str(instr[reg['PC']]))
    print("PC at " + str(reg['PC']))
    print('')
    raise

  # increment Program Counter
  reg['PC'] += 1



print(instr)
print(reg)
