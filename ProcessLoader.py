# ----------------------------------------------------------------------- #
# PROCESS LOADER
# ----------------------------------------------------------------------- #
# load example processes 'into disk'
#   simulate processes stored in disk; assign disk addresses and etc


# LIBRARIES
# ----------------------------------------- #
import binascii
import numpy as np

# user libraries/scripts

# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# PROCESS LOADER CLASS
# ----------------------------------------------------------------------- #
class ProcessLoader(object):
  def __init__(self):
    self.filename = 'eg1.npy'
    self.programsPath = './programs/'

  def LoadProcessesIntoDisk(self, disk):
    # file names/paths and memory buffer object
    # -------------------------- #
    # read in file as process; load in instructions
    program = np.load(self.programsPath + self.filename)
    # store the machine code to disk
    disk.StoreByteToDisk(program)
