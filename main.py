#!/usr/bin/env python

# MAIN file, for OS project
# Scott
# ----------------------------------------------------------------------- #

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


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #
timeslice = 10

# DISK MEMORY
# ----------------------------------------------------------------------- #
# this list will contain the entirety of the physical addresses of the disk memory
disk = Disk.Disk()


# MAIN MEMORY / REAL MEMORY
# ----------------------------------------------------------------------- #


# SAMPLE PROCESS
# ----------------------------------------------------------------------- #


# PROCESS LOADER
# ----------------------------------------------------------------------- #
# load the sample process files located in './processes' 'into disk'
ProcessLoader.LoadProcessesIntoDiskAsInstruction(disk)


# SAMPLE PROCESSOR
# ----------------------------------------------------------------------- #
# create new cpu object
cpu = CPU.CPUModel(disk)


# INSTRUCTION DECODER
# ----------------------------------------------------------------------- #




# start the cpu
cpu.start()



#print(instr)
#print(reg)
cpu.printRegisters()
