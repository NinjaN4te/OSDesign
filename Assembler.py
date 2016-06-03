# ----------------------------------------------------------------------- #
# ASSEMBLER
# ----------------------------------------------------------------------- #
# a simple assembler for converting the example programs in processes into machine code
#   store these files in processes/machine_code


# LIBRARIES
# ----------------------------------------- #

# user libraries/scripts


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# regex expressions to remove the superfluous stuff
# strip all comments, note that the comments begin with a ';' semicolon
dcomment  = '([\s]+;[\w\W\s]+)$'
# split instructions delimited by white spaces and commas
delim   = '[\s,]+'
# convert all pure numbers to base 10 (decimal) as a xmpz object from gmpy2 library
dNum = re.compile('''^(
                        [0-9]+          # starts with one or more 0-9s,
                        [0-9a-fA-F]*    # then contains zero or more 0-9a-fA-F,
                      )                 # and
                      (                 # ...
                        H|              # ends with an H (ie: hex),
                        B|              # or ends with a B (ie: binary),
                        (?<![a-fA-F])$  # or does NOT end in a-fA-F (ie: decimal)
                      )$''', re.VERBOSE)
# function call within the loading function, converts numbers to decimal base
def convertToDecimal(matchobj, arg):
  if(matchobj == None):
    # if no match, then return back original argument
    return arg
  # otherwise, convert different base numeral to decimal
  if(matchobj.group(2)=='H'):
    # Hexadecimal
    return xmpz(int(matchobj.group(1), 16))
  elif(matchobj.group(2)=='B'):
    # Binary
    return xmpz(int(matchobj.group(1), 2))
  else:
    # Decimal
    return xmpz(int(matchobj.group(1)))


def LoadProcessesIntoDiskAsInstruction(disk):
  # read in file as process; load in instructions
  with open('./processes/eg1') as file:
    ( [
      # store the instruction as byte-sized opcodes&operands to disk
      disk.StoreInstructionToDisk(
      # convert hex and binary to decimal
      [(lambda match = dNum.fullmatch(args):
            convertToDecimal(match, args))()
      # split labels from mnemonics from operands
      for args in re.split( delim,
        # remove comments
        re.sub( dcomment, '', line.rstrip('\n') )
      )])
    for line in file] )   # repeat for every line in the file,
                          #   note that every line is only one instruction in my examples
