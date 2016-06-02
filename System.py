# ----------------------------------------------------------------------- #
# SYSTEM
# ----------------------------------------------------------------------- #
# coordinate everything in this system, the CPU, hardware, buses, etc.
# will also hold the global reference to the task manager, which is very important


# LIBRARIES
# ----------------------------------------------------------------------- #
from gmpy2 import xmpz
import re

# user libraries/scripts
import constants as c
import COMMAND
import CPU
import Disk
import ProcessLoader
import TaskManager


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

class System(object):
  def __init__(self):
    self.timeslice = 10
    # create the global task manager for creating concurrent tasks
    #   note, this is NOT the same as the threads simulation we will be using later!
    self.tm = TaskManager.TaskManager()
    # DISK MEMORY
    # ----------------------------------------------------------------------- #
    # this list will contain the entirety of the physical addresses of the disk memory
    self.disk = Disk.Disk(self)

    # MAIN MEMORY / REAL MEMORY
    # ----------------------------------------------------------------------- #

    # SAMPLE PROCESS
    # ----------------------------------------------------------------------- #

    # PROCESS LOADER
    # ----------------------------------------------------------------------- #
    # load the sample process files located in './processes' 'into disk'
    ProcessLoader.LoadProcessesIntoDiskAsInstruction(self.disk)

    # SAMPLE PROCESSOR
    # ----------------------------------------------------------------------- #
    # create new cpu object
    self.cpu = CPU.CPUModel(self)

    # INSTRUCTION DECODER
    # ----------------------------------------------------------------------- #

  def Start(self):
    # create all the task objects
    # start the cpu
    self.cpu.start()
    # start the disk
    self.disk.start()
    # start the mainloop of the task manager
    self.tm.mainloop()


