# ----------------------------------------------------------------------- #
# XMPZ FUNCTIONS
# ----------------------------------------------------------------------- #
# a subclass of the xmpz class from the gmpy2 library that adds useful operations


# LIBRARIES
# ----------------------------------------- #
from gmpy2 import xmpz

# user libraries/scripts


# FUNCTIONS
# ----------------------------------------------------------------------- #

# BOOLEAN MASK OPERATIONS
# boolean AND
def maskAND(b1, b2):
  ret = xmpz(0)
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] == 1 and b2[p] == 1):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

def maskOR(b1, b2):
  ret = xmpz(0)
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] == 1 or b2[p] == 1):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

# performs maskOR directly on first argument, so 'in place'
def maskOR_in(b1, b2):
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] == 1 or b2[p] == 1):
      b1[p] = 1
    else:
      b1[p] = 0

def maskXOR(b1, b2):
  ret = xmpz(0)
  for p in range(0, max(b1.bit_length(), b2.bit_length())):
    if(b1[p] != b2[p]):
      ret[p] = 1
    else:
      ret[p] = 0
  return ret

# bitwise operations
# shifts and rotations
def leftShift(b1, n, trunc=True):
  stop = 0
  # there is no need to iterate through all the bits, only 8-n bits
  if(trunc == True):
    # get the lower value
    if(b1.bit_length()+n < 8-n):
      stop = b1.bit_length()+n
    else:
      stop = 8-n
  else:
    # don't truncate
    stop = b1.bit_length()+n
  for p in reversed(range(n,stop)):
    # shift to left by n
    b1[p] = b1[p-n]
  # set all lower bits under n to 0
  b1[:n] = 0
