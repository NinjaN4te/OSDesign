# ----------------------------------------------------------------------- #
# MICROPROCESSOR MODULES
# ----------------------------------------------------------------------- #
# keep the implementation of the microprocessor modules outside of the CPU file
#   to keep code clean


# LIBRARIES
# ----------------------------------------- #

# user libraries/scripts
import COMMAND
import constants as c
import OpCodes


# GLOBAL VARIABLES
# ----------------------------------------------------------------------- #

# MPMODULES CLASS
# ----------------------------------------------------------------------- #
# class that contains all the implementations for the different mp modules
class mpModules(object):
  def __init__(self, cpu):
    # hold a reference to the cpu object this mpModules belongs to
    self.cpu = cpu

  # MICROPROCESSOR MODULES
  # ------------------------------- #
  # refer to diagram in CPU.py for visual layout and representation
  # list:
  #   A: the accumulator register
  #   ACT: the temporary accumulator/buffer register before entering the ALU unit
  #   CU: the CU, control unit, of the microprocessor that coordinates everything in the MPU
  #   CTRL: control section of microprocessor, includes the IR, decoder, and controller sequencer
  #   FLAGS: the flags or 'F' register
  #   RAM: the block of internal registers W,Z,B,C,D,E,H,L,SP,PC
  #   TMP: the temporary register
  def A(self):
    print('A')
    yield

  def ACT(self):
    print('ACT')
    yield

  def CTRL(self):
    print('CTRL')
    yield

  # Control Unit CU
  #   the CU coordinates everything within the microprocessor. it synchronizes/sequences
  #   the entire system. it will perform the memory  fetch and decode the contents of
  #   the IR to give the correct sequence of internal and external signals for the
  #   controller sequencer to dispatch (ie: which executes the instruction)
  #   in addition, the CU also is programmed to 'know' how many words each instruction
  #   has so it fetches the correct number of bytes for every instruction. it is also
  #   the one that pipelines the instruction executions to save clock cycles, like the
  #   ADD r example in the reference, ie: whether overlap is possible. Only the CU can
  #   see the W and Z registers. it also knows when a jump was made and behaves accordingly
  # IOW, this is where most of the code is going to be.
  def CU(self):
    # the execution loop of the cpu has three phases:
    #   fetch, decode execute    --repeat ad nauseum
    #   the cpu execution will be discretely simulated using machine cycles and clock cycles.
    #   the clock cycles will also sometimes be referred to as 'states' here.
    #   one machine cycle = four clock cycles/states, notated M1,M2,... and T1,T2,... respectively
    #   so now to elaborate on each phase:
    #   FETCH:
    #     T1)
    #       address in PC is deposited onto the Address Bus to be transferred to MM. MM will then
    #         read the address on the Address Bus and decode it into some actual address of a
    #         memory location.
    #     T2)
    #       PC is incremented (PC=PC+1) which memory is reading (ie, while MM decodes and accesses
    #         the memory location at the address). At the end of T2, the contents
    #         of the memory location specified by the provided address will be available to
    #         be transferred into the MPU (microprocessing unit).
    #     T3)
    #       the instruction contained at the specified memory location is deposited onto the
    #         data bus and is transferred into the IR (instruction register) of the MPU.
    #   DECODE & EXECUTE:
    #     T4)
    #       the instruction that was transferred into the IR at the end of T3 is now
    #         decoded and executed. This takes at least one machine state (T4), but
    #         possibly more, and hence the varying number of cycles to execute a
    #         given instruction.
    #    *T5)
    #       if an instruction needs more than 4 clock cycles or states or 1 machine cycle
    #         to execute, T4 of M1 will transition directly into T1 of M2
    # create dictionary of what to do on which states/clock cycles
    def phase(arg):
      d = {
      # M1
        1:self.fetch,       # fetch instruction at address in PC
        2:self.incPC,       # increment PC
        3:self.mvINSTRtoIR, # move instruction in memory location in memory to PC
        4:self.decexec      # decode and execute function
      }
      return d.get(arg, 'ERROR')
    while(self.cpu.reg['PC'] < self.cpu.sys.disk.getNumBytes()):
      try:
        if(OpCodes.getNextOp() == True):
          # fetch new instruction
          instr = OpCodes.parseByte(self.cpu.sys.disk.GetByteAt(self.cpu.reg['PC']*c.WORD))
        else:
          # if not, then append operands to our instruction
          instr.append(OpCodes.parseByte(self.cpu.sys.disk.GetByteAt(self.cpu.reg['PC']*c.WORD)))
        # check again to see if we can execute in same cycle
        if(OpCodes.getNextOp() == True):
          # execute instruction if we have the whole instruction in memory
          instr = getattr(COMMAND, instr[1])(self.cpu.reg,instr)
      except AttributeError:
        # if failed, then throw error
        print('\n/!\\/!\\/!\\ ERROR /!\\/!\\/!\\')
        print('Error executing instruction: ' + str(instr[self.cpu.reg['PC']]))
        print('PC at ' + str(self.cpu.reg['PC']))
        print('')
        raise

      # increment Program Counter
      self.cpu.reg['PC'] += 1

      phase(self.cpu.ccycle)()
      self.cpu.runClock()
      yield

  def RAM(self):
    print('RAM')
    yield

  def TMP(self):
    print('TMP')
    yield


  # CU FUNCTIONS
  # ------------------------------- #
  def fetch(self):
    # deposit PC onto Address Bus
    #   destination is memory
    self.cpu.addressBus.deposit(self.cpu.reg['PC'], c.mCU, c.mMM)
    print('fetch')
  def incPC(self):
    print('incPC')
    pass
  def mvINSTRtoIR(self):
    print('mvINSTRtoIR')
    pass
  def decexec(self):
    print('decexec')
    pass

