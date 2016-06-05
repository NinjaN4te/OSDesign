# ----------------------------------------------------------------------- #
# DISK
# ----------------------------------------------------------------------- #
# a class to keep disk memory related things together for


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/scripts
import constants as c


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

  # StoreByteToDisk
  # called from LoadProcessesIntoDisk() from ProcessLoader.
  #   args: a byte of data, which is a machine code instruction,
  #   and then stores it as machine code 'to disk'
  def StoreByteToDisk(self, program):
    # transfer into disk.
    #   for the purposes of the simulation, these processes will
    #   be stored sequentially on disk. Possibility for change at later time (?)
    # convert to binary representation
    binprogram = np.unpackbits(program.astype(np.uint8))
    # store binary sequence on disk
    self.diskMem[self.index:self.index+binprogram.size] = binprogram
    # increment the index to next available address
    self.index += binprogram.size
    # increase the number of bytes occupied on disk
    self.numBytes += program.size

  def GetByteAt(self, index):
    # return a byte sized view displaced by index
    return self.diskMem[index:index+c.WORD]

  def start(self):
    # create the new task for this disk object
    self.sys.tm.new(self.run())

  # the run loop of the disk in the program
  def run(self):
    yield

