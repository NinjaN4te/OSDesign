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
# numpy already implements AND, OR, and XOR
# bitwise equivalence function, which is the complement of XOR
#   ie: for x->y, true on x=y and false otherwise
#       iow: true on (1,1) or (0,0); false on (1,0) or (0,1)
def bitwise_eqv(b1, b2):
  return np.invert(np.bitwise_xor(b1, b2))

# bitwise operations
# shifts and rotations
# shifts all bits over left by n bits, replaces lower n bits with zeros
def leftShift(b1, n):
  # note, numpy access arrays from left to right, iow, 0 is leftmost,
  #   but the binary represenations themselves are big-endian, ie: higher bits are to the left
  shift(b1, n*-1, output=b1, cval=0)

def add(b1, n):
  temp = np.packbits(b1)[0]
  sum = np.array([temp + n], dtype=np.uint8)
  return np.unpackbits(sum)
