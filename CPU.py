# ----------------------------------------------------------------------- #
# CPU
# ----------------------------------------------------------------------- #
# a (simplified) model of the microprocessor cpu
# with generous amounts of references from:
#   http://www.msxarchive.nl/pub/msx/mirrors/msx2.com/zaks/z80prg02.htm


# LIBRARIES
# ----------------------------------------- #
from gmpy2 import xmpz

# user libraries/scripts
import constants as c
import COMMAND
import Disk
import OpCodes
import xmpzfunctions as xf


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #


# CPU MODEL CLASS
# ----------------------------------------------------------------------- #
#
#           Diagram of CPU layout
#                                                                                .--.
#                                                               8 BITS           |B | .  .
#       .------------------------------------------------------------------------|U |/'--'\ DATA
#       |.-------------------. .-------------------------. .----------------.----|F |\.--./  BUS
#       ||                   | |                /\       | |        /\     / \   |F | '  '
#       ||                   | |               /..\      | |       /..\   /. .\  |E |
#       ||                 __| |__              ||       | |        ||     | |   |R |
#      \''/               |  MUX  |             ||   .---+-+---.   \''/    | |   '--'
#       \/               /'-------'\            ||   |    A    |  ._\/_.   | |
#   .--------.          / /       \ \           ||   '---+-+---'  |TEMP|   | |
#   |   IR   |      .--'-'---------'-'--.       ||       | |      '-_.-'   | |
#   '--------'      |    W    |    Z    |       ||   .---+-+---.    ||     | |
#       ||          |---------+---------|       ||   |   ACT   |    ||     | |
#      \''/         |    B    |    C    |       ||   '---+-+---'    ||     | |
#       \/          |---------+---------|       ||       | |        ||     | |
#   .--------.      |    D    |    C    |       ||       | |       \''/    | |
#   | DECODR |      |---------+---------|       ||      _|_|_     __\/.    | |
#   '--------'      |    H    |    L    |       ||       \   \   /   /     | |
#       ||          |-------------------|       ||        \   \ /   /      | |
#      \''/         |        S P        |   .--------.     \   '   /       | |
#       \/          |    STACK PTR      |   | FLAGS  |<---- \ ALU /        | |
#   .--------.      |-------------------|   '--------'       \___/         | |
#   | CTRLLR |      |        P C        |                     | |          | |
#   | SEQNCR |      |    PRGRM CNTRL    |                     | '----------' |
#   '--------'      '-------------------'                     '--------------'
#    /\    /\                | |
#   /..\  /..\               | |
#    ||    ||                | |                                                 .--.
#    ||    ||                | |                                                 |B |
#    ||    ||                | |                                                 |U |
#    ||    ||                | |                               16 BITS           |F |  .
#    ||    ||                | '-------------------------------------------------|F |--'\ ADDRESS
#    ||    ||                '---------------------------------------------------|E |--./   BUS
#    ||    ||                                                                    |R |  '
#    ||    ||                                                                    '--'
#    ||    ||____________________________________________________________________________  \
#    ||    '----------------------------------------------------------------------------+   | CONTROL
#    ||                                                                                 .   -
#    |'---------------------------------------------------------------------------------'\  ' SIGNALS
#    '----------------------------------------------------------------------------------./  |
#                                                                                       '  /
#

# a generic bus object
#   define the size of the bus, most probably will be c.WORD.
#   these buses also have concurrency so they can transfer data concurrently
class GenericBus(object):
  def __init__(self, size):
    # size of the bus
    self.size = size
    # the data deposited in the bus
    self.bus = xmpz(0)

  # deposit data into the bus to transfer around
  def deposit(self, data):
    self.bus[:] = 0   # clear bus
    xf.maskOR_in(self.bus, data, ret=false)

  # read data in the bus; return the data
  def read(self):
    return self.data

class CPUModel(object):
  def __init__(self, disk):
    # clock cycles
    self.clock = 0
    # create buses
    self.addressBus = GenericBus(16)
    self.dataBus = GenericBus(c.WORD)
    # give cpu a reference to disk, for now
    self.disk = disk

    #   REGISTERS
    self.reg = {
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

  # fetch decode execute
  def fde(self):
    while(self.reg['PC'] < self.disk.getNumBytes()):
      try:
        if(OpCodes.getNextOp() == True):
          # fetch new instruction
          #print('{:02X}'.format(self.disk.GetByteAt(reg['PC']*c.WORD)))
          instr = OpCodes.parseByte(self.disk.GetByteAt(self.reg['PC']*c.WORD))
        else:
          # if not, then append operands to our instruction
          instr.append(OpCodes.parseByte(self.disk.GetByteAt(self.reg['PC']*c.WORD)))
        # check again to see if we can execute in same cycle
        if(OpCodes.getNextOp() == True):
          # execute instruction if we have the whole instruction in memory
          instr = getattr(COMMAND, instr[1])(self.reg,instr)
      except AttributeError:
        # if failed, then throw error
        print('\n/!\\/!\\/!\\ ERROR /!\\/!\\/!\\')
        print('Error executing instruction: ' + str(instr[self.reg['PC']]))
        print('PC at ' + str(self.reg['PC']))
        print('')
        raise

      # increment Program Counter
      self.reg['PC'] += 1


  # start the cpu
  def start(self):
    self.fde()

  # CONVENIENCE FUNCTIONS
  # ----------------------------------------------------------------------- #
  def printRegisters(self):
    print(
      # general registers
      'A: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['A'])) + '\n' + 
      'B: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['B'])) + '\n' + 
      'C: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['C'])) + '\n' + 
      'D: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['D'])) + '\n' + 
      'E: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['E'])) + '\n' + 
      'H: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['H'])) + '\n' + 
      'L: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(int(self.reg['L'])) + '\n'
    )
    # flag register
    print('   ZNHC0000')
    print('F: {:0>8b}'.format(int(self.reg['F'])))



