# ----------------------------------------------------------------------- #
# DISK
# ----------------------------------------------------------------------- #
# a class to keep disk memory related things together for


# LIBRARIES
# ----------------------------------------- #
from gmpy2 import xmpz

# user libraries/scripts
import constants as c


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# DISK CLASS
# ----------------------------------------------------------------------- #
class Disk(object):
  def __init__(self):
    # this member will contain the entirety of the physical addresses of the disk memory
    self.diskMem = xmpz(0)
    # index to the next free actual physical address of diskMem
    #   for purposes of the simulation, currently only increments, ie: only sequentially storing
    self.index = 0

  def getDiskMem(self):
    return self.diskMem
