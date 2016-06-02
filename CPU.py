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
import mpModules
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
    # source and destination modules, use with constants in the constants.py file
    self.src = ''
    self.dst = ''
    # if bus is being used, it is busy and cannot be used by some other module
    self.busy = False

  # deposit data into the bus to transfer around
  def deposit(self, data, src, dst):
    self.bus[:] = 0   # clear bus
    xf.maskOR_in(self.bus, data, ret=false)
    self.src=src
    self.dst=dst

  # read data in the bus; return the data
  def read(self):
    return self.data

class CPUModel(object):
  def __init__(self, system):
    # clock cycles, also called states
    self.ccycle = 1
    # machine cycles, 4 clock cycles = 1 machine cycle
    self.mcycle = 1
    # create buses
    self.addressBus = GenericBus(16)
    self.dataBus = GenericBus(c.WORD)
    # hold a reference to the system object to which this class belongs to
    self.sys = system
    # implementation of microprocessor modules of the cpu are kept separate
    #   so create an object of it here
    self.modules = mpModules.mpModules(self)

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
        'IR': 0,  # Instruction Register, stores copy of instruction to be executed
        'PC': 0   # Program Counter register, holds address of next instruction to be executed
    }

  # start the cpu
  def start(self):
    # --- #
    # create all the modules of the microprocessor as separate concurrent tasks.
    #   refer to diagram above

    self.sys.tm.new(self.modules.A())   # A
    self.sys.tm.new(self.modules.ACT()) # ACT
    self.sys.tm.new(self.modules.CU())  # CU, control unit
    self.sys.tm.new(self.modules.CTRL())# CTRL, control section
    self.sys.tm.new(self.modules.RAM()) # RAM
    self.sys.tm.new(self.modules.TMP()) # TMP
    # --- #

  # increment the clock cycles (or states) and the machine cycles.
  #   here 4 clock cycles = 1 machine cycles
  #   this is our discrete time quantum
  def runClock(self):
    self.ccycle += 1
    if(self.ccycle > 4):
      self.ccycle -= 4
      self.mcycle += 1

  # reset the machine and clock cycle counters,
  #   call at beginning of every new instruction fetching
  def resetClock(self):
    self.ccycle = 1
    self.mcycle = 1

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



