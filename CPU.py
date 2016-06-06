# ----------------------------------------------------------------------- #
# CPU
# ----------------------------------------------------------------------- #
# a (simplified) model of the microprocessor cpu
# with generous amounts of references from:
#   http://www.msxarchive.nl/pub/msx/mirrors/msx2.com/zaks/z80prg02.htm


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/scripts
import constants as c
import Disk
from mpModules import CLK, CU


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #


# CPU MODEL CLASS
# ----------------------------------------------------------------------- #
#
#           Diagram of CPU layout   {{{2
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
#    ||    ||                *                                                   |R |  '
#    ||    ||                                                                    '--'
#    ||    ||____________________________________________________________________________  \
#    ||    '----------------------------------------------------------------------------+   | CONTROL
#    ||                                                                                 .   -
#    |'---------------------------------------------------------------------------------'\  ' SIGNALS
#    '----------------------------------------------------------------------------------./  |
#                                                                                       '  /
#}}}2

# a generic bus object
#   define the size of the bus, most probably will be c.WORD.
#   these buses also have concurrency so they can transfer data concurrently
class GenericBus(object):
  def __init__(self, size):
    # size of the bus
    self.size = size
    # the bus will hold data to be transferred between modules
    self.data = np.zeros(size, dtype=np.uint8)

  # deposit data into the bus to transfer around
  def deposit(self, data):
    self.data.fill(0)   # clear bus
    self.data[0:data.size] = data

  # read data in the bus; return the data
  def read(self):
    return self.data

class CPUModel(object):
  def __init__(self, system):
    # current clock cycle. increase machine cycle by 1 every 4 clock cycles
    #   ie: machine cycle switches high/low every 2 clock cycles
    self.ccycle = 1
    # clock counter and clock frequency
    # the gameboy's cpu speed is technically 1 clock cycle = 4.19MHz
    self.clock = 0
    self.clockSpeed = 4

    # create buses
    self.addressBus = GenericBus(16)      # specifies address/destination of data
    self.dataBus    = GenericBus(c.WORD)  # actual data to transfer
    self.controlLines = np.zeros(8)       # i/o pins to syncronize EVERYTHING
    # hold a reference to the system object to which this class belongs to
    self.sys = system
    # implementation of microprocessor modules of the cpu are kept separate

    #   REGISTERS
    self.reg = {
      # general purpose registers
        'A' : np.zeros(c.WORD, dtype=np.uint8),
        'B' : np.zeros(c.WORD, dtype=np.uint8),
        'C' : np.zeros(c.WORD, dtype=np.uint8),
        'D' : np.zeros(c.WORD, dtype=np.uint8),
        'E' : np.zeros(c.WORD, dtype=np.uint8),
        'H' : np.zeros(c.WORD, dtype=np.uint8),
        'L' : np.zeros(c.WORD, dtype=np.uint8),
      # hidden registers, used by the control unit
      #   when 'concatenated', together they form one 16-bit address, WZ
      #   note: W is the higher half, Z is the lower half
        'W' : np.zeros(c.WORD, dtype=np.uint8),
        'Z' : np.zeros(c.WORD, dtype=np.uint8),
      # special registers
        'F' : np.zeros(c.WORD, dtype=np.uint8),   # Flag register
        'SP': np.zeros(c.DWORD, dtype=np.uint8),  # Stack Pointer register
        'IR': np.zeros(c.WORD, dtype=np.uint8),   # Instruction Register,
                                                  #   stores copy of instruction to be executed
        'PC': np.zeros(c.WORD, dtype=np.uint8)    # Program Counter register,
                                                  #   holds address of next instruction to be executed
    }

  # start the cpu
  def start(self):
    # --- #
    # create all the modules of the microprocessor as separate concurrent tasks.
    #   refer to diagram above

    #self.sys.tm.new(self.modules.A())   # A
    #self.sys.tm.new(self.modules.ACT()) # ACT
    #self.sys.tm.new(self.modules.CTRL())# CTRL, control section
    #self.sys.tm.new(self.modules.RAM()) # RAM
    #self.sys.tm.new(self.modules.TMP()) # TMP
    self.sys.tm.new(CU(self))  # CU, control unit
    self.sys.tm.new(CLK(self)) # CLK, clock
    # note, tasks added last get executed first!
    # --- #

  # increment the clock cycles (or states) and the machine cycles.
  #   here 4 clock cycles = 1 machine cycles
  #   this is our discrete time quantum
  def runClock(self):
    self.clock += 1
    if(self.clock > self.clockSpeed):
      self.clock -= self.clockSpeed
      self.ccycle += 1
      if(self.ccycle == 3):
        # flip the bit
        self.controlLines[c.CLK] = (self.controlLines[c.CLK]<1)
      elif(self.ccycle > 4):
        # flip the bit
        self.controlLines[c.CLK] = (self.controlLines[c.CLK]<1)
        self.ccycle -= 4

  # reset the machine and clock cycle counters,
  #   call at beginning of every new instruction fetching
  def resetClock(self):
    self.ccycle = 1

  # a convenience function, ask whether or not we have finished
  #   reading the process from the disk and whether the clock has
  #   run all its course
  def pcEnd(self):
    if(np.packbits(self.reg['PC'])[0] <= self.sys.disk.getNumBytes()*c.WORD):
      return False
    else:
      return True
    

  # CONVENIENCE FUNCTIONS
  # ----------------------------------------------------------------------- #
  def printRegisters(self):
    print(
      # general registers
      'A: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['A'])[0]) + '\n' + 
      'B: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['B'])[0]) + '\n' + 
      'C: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['C'])[0]) + '\n' + 
      'D: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['D'])[0]) + '\n' + 
      'E: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['E'])[0]) + '\n' + 
      'H: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['H'])[0]) + '\n' + 
      'L: {0:>4d}  {0:0>8b}  {0:^#6x}'.format(np.packbits(self.reg['L'])[0]) + '\n'
    )
    # flag register
    print('   ZNHC0000')
    print('F: {:0>8b}'.format(np.packbits(self.reg['F'])[0]))



