
# multicore simulation
from collections import deque
import numpy as np
import re
from abc import ABCMeta


# define some random constants for use in code
NUMPROCESSORS = 8
FILEPATH = './DataFile7.txt'
TIMEQ = 10
INCOMPLETE = 0
COMPLETE = 1
GOOD = 2
INTERRUPT = 3
QUIT = 4

# library stuff {{{2
class CoroutineType(metaclass=ABCMeta):
  # define the abstract property/attribute _task, which is a reference
  #   to the task which is executing a coroutine of the run() function
  #   in an instance of this coroutinetype class
  def get_task(self):
    return self._task
  def set_task(self, newtask):
    self._task = newtask
  @classmethod
  def __subclasshook__(cls, C):
    if cls is CoroutineType:
      # a class is a virtual subclass of CoroutineType if it contains a method
      #   'run()' in itself or any of its base classes
      if any('run' in B.__dict__ for B in C.__mro__):
        return True
    return NotImplemented

class Task(object):
  taskid = 0
  def __init__(self, target, tm):
    Task.taskid += 1
    self.tid      = Task.taskid   # Task ID
    self.target   = target        # Target coroutine
    self.sendval  = None          # Value to send
    self.tm       = tm            # reference to task manager of this task
    self.children = deque()       # tid's of tasks spawned off of this task
  def run(self):
    return self.target.send(self.sendval)
  def new(self, target):
    # add new child task, if this parent task dies, all the children go with it
    child = self.tm.new(target, obj=True)
    self.children.append(child)
  def killChildren(self):
    for child in self.children:
      child.target.close()

class TaskManager(object):
  def __init__(self):
    # queue of tasks to run
    self.queue    = deque()
    # a dictionary that holds the task and id while they are not closed
    self.taskmap  = {}

  def addToQueue(self, task):
    self.queue.append(task)
  def reAddToQueue(self, task):
    self.queue.appendleft(task)

  # add a new task to append to the queue
  def new(self, target, obj=False):
    try:
      # a CoroutineType
      newtask = Task(target.run(), self)
      self.taskmap[newtask.tid] = newtask
      self.addToQueue(newtask)
      target.set_task(newtask)
      if(obj==True):
        return newtask
      return newtask.tid
    except AttributeError:
    # some regular generator object
      newtask = Task(target, self)
      self.taskmap[newtask.tid] = newtask
      self.addToQueue(newtask)
      if(obj==True):
        return newtask
      return newtask.tid

  def exit(self, task):
    # task has terminated, remove it from the dictionary
    # check if task has any children
    task.killChildren()
    self.taskmap.pop(task.tid, 'None')
    #raise
    #del self.taskmap[task.tid]

  # main loop, pop off the next task, run it, and then append left
  def mainloop(self):
    # run while there are still tasks in the dictionary
    while self.taskmap:
      task = self.queue.pop()
      # run until task completely finishes execution
      try:
        result = task.run()
      except StopIteration:
        # catch tasks completing and call the exit function, then move on to next task
        self.exit(task)
        continue
      self.reAddToQueue(task)

#}}}2

class Clock(CoroutineType):
  def __init__(self, sys):
    self.sys = sys
    self.time = 0
    self.cntr = 0
  def advanceTime(self):
    self.time += 1
    self.cntr += 1
    if(self.cntr > TIMEQ):
      self.cntr -= TIMEQ
      self.sys.generateInterrupt()
    if(self.time > 10000):
      self.sys.generateQUIT()
  def getT(self):
    return self.time
  def run(self):
    while(True):
      self.advanceTime()
      status = yield from sys.getSysStatus()
      if status == QUIT:
        break

# multicore chip class
#   the workhorse that splits the load
class MultiCoreProcessor(CoroutineType):
  def __init__(self, sys):
    self.sys = sys
    # list of processors in this multicore setup
    self.processors = [Processor(self, i) for i in range(0, NUMPROCESSORS)]
    self.pload = np.zeros(NUMPROCESSORS)
    self.queue = deque()
  def admitNewProcess(self, process):
    p = np.argmin(self.pload, axis=0)
    self.processors[p].admitNewProcess(process)
  def start(self):
    for p in self.processors:
      self.get_task().new(p)
    
  def run(self):
    while(True):
      if(len(self.queue) >0):
        newp = self.queue.pop()
        self.admitNewProcess(newp)
      status = yield from sys.getSysStatus()
      if status == QUIT:
        break

# the processor class
class Processor(CoroutineType):
  def __init__(self, mcp, prcrid):
    # id of the processor
    self.mcp = mcp
    self.prcrid = prcrid
    self.jobslist = deque()
    self.load = 0
  def getLoad(self):
    return self.load
  def admitNewProcess(self, process):
    self.jobslist.append(process)
    self.load += process.totalPTime
  def run(self):
    while(True):
      # update load
      self.mcp.pload[self.prcrid] = self.getLoad()
      if(len(self.jobslist)>0):
        self.jobslist[0].run()
      status = yield from sys.getSysStatus()
      if status == INTERRUPT:
        if(len(self.jobslist)>0):
          self.jobslist.append(self.jobslist.popleft())
      elif status == QUIT:
        break

# the process class
class Process():
  def __init__(self, pid, arrivalt, instr):
    self.pid = pid
    self.arrivalt = arrivalt
    self.instr = instr
    self.totalTime = np.sum(instr, axis=0)
    self.totalPTime = np.sum(instr[::2], axis=0)
    self.totalWTime = np.sum(instr[1::2], axis=0)
    self.index = 0
  def run(self):
    try:
      self.instr[self.index] -= TIMEQ
      if(self.instr[self.index]<0):
        self.index+=1
        self.instr[self.index] += self.instr[self.index-1]
    except IndexError:
      return COMPLETE

# contains the list of processes to process through
class Jobs(CoroutineType):
  def __init__(self, sys):
    self.jobslist = deque()
    self.sys = sys
  def loadProcessesFromFile(self, path):
    with open(path) as f:
      for line in f:
        # remove newlines and trailing commas, whitespaces, etc
        line = re.sub('[\s\n,]+$', '', line)
        # split by commas and whitespace
        line = re.split('[\s,]+', line)
        self.jobslist.append(Process(int(line[0]), int(line[1]), np.fromiter((int(t) for t in line[2:]), dtype=np.int16)))
    f.close()
  def run(self):
    while(True):
      try:
        if(self.jobslist[0].arrivalt <= self.sys.clock.getT()):
          newjob = self.jobslist.popleft()
          self.sys.mcp.queue.append(newjob)
          print('admitted new job @ {:}'.format(self.sys.clock.getT()))
        status = yield from sys.getSysStatus()
        if status == QUIT:
          break
      except IndexError:
        break

class System():
  def __init__(self):
    self.clock = Clock(self)
    self.jobs = Jobs(self)
    self.mcp = MultiCoreProcessor(self)
    self.tm = TaskManager()
    self.jobs.loadProcessesFromFile(FILEPATH)
    self.status = GOOD
  def start(self):
    # start all tasks
    self.tm.new(self.mcp)
    self.mcp.start()
    self.tm.new(self.jobs)
    self.tm.new(self.clock)
    self.tm.mainloop()
  def generateInterrupt(self):
    self.status = INTERRUPT
  def generateQUIT(self):
    self.status = QUIT
  def getSysStatus(self):
    subStatus = yield
    if subStatus == None:
      return self.status
    

sys = System()
sys.start()
