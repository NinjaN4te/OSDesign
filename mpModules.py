# ----------------------------------------------------------------------- #
# MICROPROCESSOR MODULES
# ----------------------------------------------------------------------- #
# keep the implementation of the microprocessor modules outside of the CPU file
#   to keep code clean


# LIBRARIES
# ----------------------------------------- #
import numpy as np

# user libraries/scripts
import BinaryFunctions as bf
import ControllerSequencer
import constants as c
from CoroutineType import CoroutineType
import Decoder


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# MPMODULES CLASS
# ----------------------------------------------------------------------- #
# class that contains all the implementations for the different mp modules
#class mpModules(object):
#  def __init__(self, cpu):
    # hold a reference to the cpu object this mpModules belongs to
#    self.cpu = cpu

  # MICROPROCESSOR MODULES
  # ------------------------------- #
  # refer to diagram in CPU.py for visual layout and representation
  # list:
  #   A: the accumulator register
  #   ACT: the temporary accumulator/buffer register before entering the ALU unit
  #   CLK: keeps the clock running
  #   CU: the CU, control unit, of the microprocessor that coordinates everything in the MPU
  #   CTRL: control section of microprocessor, includes the IR, decoder, and controller sequencer
  #   FLAGS: the flags or 'F' register
  #   RAM: the block of internal registers W,Z,B,C,D,E,H,L,SP,PC
  #   TMP: the temporary register
class A():
  def __init__(self):
    pass
  #yield

class ACT():
  def __init__(self):
    pass
  #yield

class CLK(CoroutineType):
  def __init__(self, cpu):
    self.cpu = cpu
  def run(self):
    while(True):
      #print(' {0:}.{1:}'.format(self.cpu.ccycle, self.cpu.clock))
      #print('pc: {:}'.format(np.packbits(self.cpu.reg['PC'])[0]))
      # run the clock to sync all other tasks
      self.cpu.runClock()
      if(self.cpu.pcEnd() == True):
        break
      else:
        yield

class CTRL():
  def __init__(self):
    pass
  #yield

  # Control Unit CU
  #   the CU coordinates everything within the microprocessor. it synchronizes/sequences
  #   the entire system. it will perform the memory  fetch and decode the contents of
  #   the IR to give the correct sequence of internal and external signals for the
  #   controller sequencer to dispatch (ie: which executes the instruction)
  #   in addition, the CU also is programmed to 'know' how many words each instruction #   has so it fetches the correct number of bytes for every instruction. it is also
  #   the one that pipelines the instruction executions to save clock cycles, like the
  #   ADD r example in the reference, ie: whether overlap is possible. Only the CU can
  #   see the W and Z registers. it also knows when a jump was made and behaves accordingly
  # IOW, this is where most of the code is going to be.
class CU(CoroutineType):
  def __init__(self, cpu):
    # hold a reference to the cpu object that created this object
    self.cpu = cpu
    # the actual instruction, hold temporarily here if we have to wait for its operands
    self.instr = ''
    # controller sequencer module
    self.ctrlSeq = ControllerSequencer.ControllerSequencer(self)
    # the decoder module that will decode and interpret instructions
    #   loaded into IR from memory, which are is binary machine code
    self.decoder = Decoder.Decoder(self)
    # the next external operation to perform: M1R, RD, MWR, etc
    self.nextOp = 'M1R'
    # the execution loop of the cpu has three phases:
    #   fetch, decode execute    --repeat ad nauseum
    #   the cpu execution will be discretely simulated using machine cycles and clock cycles.
    #   the clock cycles will also sometimes be referred to as 'states' here.
    #   one machine cycle = four clock cycles/states, notated m1,m2,... and t1,t2,... respectively
    #   so now to elaborate on each phase:
    #   fetch:
    #     t1)
    #       address in pc is deposited onto the address bus to be transferred to mm. mm will then
    #         read the address on the address bus and decode it into some actual address of a
    #         memory location.
    #     t2)
    #       pc is incremented (pc=pc+1) which memory is reading (ie, while mm decodes and accesses
    #         the memory location at the address). at the end of t2, the contents
    #         of the memory location specified by the provided address will be available to
    #         be transferred into the mpu (microprocessing unit).
    #     t3)
    #       the instruction contained at the specified memory location is deposited onto the
    #         data bus and is transferred into the ir (instruction register) of the mpu.
    #   decode & execute:
    #     t4)
    #       the instruction that was transferred into the ir at the end of t3 is now
    #         decoded and executed. this takes at least one machine state (t4), but
    #         possibly more, and hence the varying number of cycles to execute a
    #         given instruction.
    #    *t5)
    #       if an instruction needs more than 4 clock cycles or states or 1 machine cycle
    #         to execute, t4 of m1 will transition directly into t1 of m2
    # create dictionary of what to do on which states/clock cycles
  def operation(self, arg):
    d = {
      '...' :self.wait,   # do nothing if next is '...'
      'M1R' :self.M1R,    # machine cycle 1 fetch and decode
      'RD'  :self.RD      # read from memory
    }
    return d.get(arg, 'ERROR') 
  # the run function used by the task manager
  def run(self):
    while(True):
      self.get_task().new(self.operation(self.nextOp)())
      # setting to <4 allows T2 of the machine cycle to increment the PC!
      # suspend the run until we are at the beginning of each clock cycle
      while(self.cpu.clock < 4):
        if(self.cpu.pcEnd() == True):
          break
        yield
      if(self.cpu.pcEnd() == True):
        break
      yield

  # CU EXTERNAL OPERATIONS
  # ------------------------------- #
  def M1R(self):
    print('                               m1r')
    # the basic Machine Cycle 1 run of fetching the next byte of data
    # what to do at each clock phase
    if(self.cpu.ccycle==1):
      # deposit PC onto address bus, PC OUT STATUS
      self.cpu.addressBus.deposit(self.cpu.reg['PC'])
      print('ADDRESSBUS: {:}'.format(self.cpu.addressBus.read()))
      # /RD goes low (active)
      self.cpu.controlLines[c.RD] = c.LO
    elif(self.cpu.ccycle==2):
      # increment Program Counter
      self.cpu.reg['PC'] = bf.add(self.cpu.reg['PC'], c.WORD)
      # memory uses one clock cycle to decode address and make contents available
    elif(self.cpu.ccycle==3):
      # wait a little for memory to transfer on data bus first
      yield
      # transfer byte of data from memory to IR
      self.cpu.reg['IR'] = np.copy(self.cpu.dataBus.read())
      print('IR: {:}'.format(self.cpu.reg['IR']))
      # set /RD back to hi (inactive)
      self.cpu.controlLines[c.RD] = c.HI
    elif(self.cpu.ccycle==4):
      # decode new instruction in IR, and execute if possible
      #   result is stored in instr
      self.decoder.parseByte(self.cpu.reg['IR'], self.nextOp)
      print('INSTR: {:}'.format(self.instr))
      # execute new instruction if no more operands to wait for
      #  self.decoder.executeSeq(self.instr, byte)

  def RD(self):
    print('                               rd')
    # read from memory
    if(self.cpu.ccycle==1):
      # deposit PC onto address bus, PC OUT STATUS
      self.cpu.addressBus.deposit(self.cpu.reg['PC'])
      print('ADDRESSBUS: {:}'.format(self.cpu.addressBus.read()))
      # /RD goes low (active)
      self.cpu.controlLines[c.RD] = c.LO
    elif(self.cpu.ccycle==2):
      # increment Program Counter
      self.cpu.reg['PC'] = bf.add(self.cpu.reg['PC'], c.WORD)
      # memory uses one clock cycle to decode address and make contents available
    elif(self.cpu.ccycle==3):
      # wait a little for memory to transfer on data bus first
      yield
      # transfer byte of data from memory to destination register
      # decode the data on the bus
      data = self.decoder.parseByte(self.cpu.dataBus.read(), self.nextOp)
      # then store in appropriate register, as gated by the MUX
      self.cpu.reg[self.mux()] = np.copy(data)
      print('DATABUS: {:}'.format(data))
      print('MUX: {:}'.format(self.mux()))
      # set /RD back to hi (inactive)
      self.cpu.controlLines[c.RD] = c.HI
      print('reg[{0:}] loaded with: {1:}'.format(self.mux(), self.cpu.reg[self.mux()]))
    elif(self.cpu.ccycle==4):
      print('PASS 4')
      # nothing
      pass
    
  # make sure that this is called if there are empty clock cycles left
  def wait(self):
    self.nextOp = 'M1R'
    pass
    # this yield will not be reached
    yield
      

  # the multiplexer MUX that selects the destination register
  def mux(self):
    return c.DESTINATION[np.array_str(self.instr[2:5])]

class RAM():
  def __init__(self):
    pass
  #yield

class TMP():
  def __init__(self):
    pass
  #yield



