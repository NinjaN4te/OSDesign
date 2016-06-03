# ----------------------------------------------------------------------- #
# DISK
# ----------------------------------------------------------------------- #
# a class to keep disk memory related things together for


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/scripts
import constants as c
import OpCodes


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# DISK CLASS
# ----------------------------------------------------------------------- #
class Disk(object):
  def __init__(self, system):
    # this member will contain the entirety of the physical addresses of the disk memory
    self.diskMem = np.zeros(c.DISKSIZE, dtype=np.byte)
    # index to the next free actual physical address of diskMem
    #   for purposes of the simulation, currently only increments, ie: only sequentially storing
    self.index = 0
    # keep track of size of diskMem in terms of bytes
    self.numBytes = 0
    # hold a reference to the system object this class belongs to
    self.sys = system

  # return the disk memory object
  def getDiskMem(self):
    return self.diskMem

  # return the number of bytes occupying the disk memory
  def getNumBytes(self):
    return self.numBytes

  # called from StoreInstructionToDisk
  #   simply transfer the byte into a byte sized window starting at self.index
  # args:
  #   byte: a ConstBitArray
  def storeProcessInDiskMemory(self, byte):
    # iterate over ConstBitStream, transfer into disk.
    #   for the purposes of the simulation, these processes will
    #   be stored sequentially on disk. Possibility for change at later time (?)
      # note, ConstBitStream reads left to right! ie: it 'appears' like little-endian
    #self.diskMem[self.index:self.index+c.WORD] = byte
    self.diskMem[self.index:self.index+byte.size] = byte
    # increment the index to next available address
    #self.index += c.WORD
    self.index += byte.size
    self.numBytes += 1
    

  # StoreInstructionToDisk
  # called from LoadProcessesIntoDiskAsInstruction() from the ProcessLoader module.
  #   this takes as an argument a single line of an instruction from that function
  #   and then stores it as machine code 'to disk'
  def StoreInstructionToDisk(self, instr):
    try:
      # convert instruction into opcode & operands,
      #   which is pure binary, ie: machine code
      bytelist = getattr(OpCodes, instr[ c.MNEMONIC ])(instr)
    except AttributeError:
      # if failed, then throw error
      print('\n/!\\/!\\/!\\ ERROR /!\\/!\\/!\\')
      print('Error in storing instruction: ' + str(instr))
      print('')
      raise

    for byte in bytelist:
      self.storeProcessInDiskMemory(byte)

  def GetByteAt(self, index):
    # return a byte sized view displaced by index
    return self.diskMem[index:index+c.WORD]

  def start(self):
    # create the new task for this disk object
    self.sys.tm.new(self.run())

  # the run loop of the disk in the program
  def run(self):
    yield

