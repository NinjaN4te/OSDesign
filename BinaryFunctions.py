# ----------------------------------------------------------------------- #
# BINARY FUNCTIONS
# ----------------------------------------------------------------------- #
# useful binary operations for numpy arrays used as bit arrays


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/scripts


# FUNCTIONS
# ----------------------------------------------------------------------- #

# BOOLEAN MASK OPERATIONS
# numpy already implements these

# bitwise operations
# shifts and rotations
# shifts all bits over left by n bits, replaces lower n bits with zeros
def leftShift(b1, n):
  np.roll(b1, n*-1)
  # set all lower bits under n to 0
  # note, numpy access arrays from left to right, iow, 0 is leftmost,
  #   but the binary represenations themselves are big-endian, ie: higher bits are to the left
  b1[b1.size-n:b1.size] = 0
