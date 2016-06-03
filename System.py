# ----------------------------------------------------------------------- #
# SYSTEM
# ----------------------------------------------------------------------- #
# coordinate everything in this system, the CPU, hardware, buses, etc.
# will also hold the global reference to the task manager, which is very important


# LIBRARIES
# ----------------------------------------------------------------------- #
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

# notes to self
# in Disk.py, we store in values simply by copying them in straight via assignment
#   which would mean that the disk grows to the 'right' (or positive direction, in general)
#   while the bit representation itself is by default big-endian. Which may be
#   a little confusing, potentially, so perhaps clear that up a little
#   ... checked with random tests. copying it from [startindex:startindex+sizedata]
#         is the correct way to handle this; to keep packbits binary values the same
# check if classes created within a class can access variables in the higher class
#   without needing to get a reference to the higher reference itself.
#   ie: reg['F'] instead of self.cpu.reg['F'], where cpu is a reference to some CPU
#     class that created the current object, and we wish to access this higher cpu
#     class's reg variable
