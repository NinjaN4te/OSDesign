#!/usr/bin/env python

# MAIN file, for OS project
# Scott
# ----------------------------------------------------------------------- #

# LIBRARIES
# ----------------------------------------------------------------------- #
# user libraries/scripts
import System

# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #


# create a system object and let it handle the rest
sys = System.System()
sys.Start()

sys.cpu.printRegisters()
