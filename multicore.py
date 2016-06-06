
# multicore simulation
from collections import deque
import numpy as np
import re
from abc import ABCMeta


# define some random constants for use in code
NUMPROCESSORS = 8
FILEPATH = './DataFile7.txt'
TIMEQ = 1

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
    #print('running pid {:}'.format(self.tid))
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
  def advanceTime(self):
    self.time += TIMEQ
  def getT(self):
    return self.time
  def run(self):
    while(True):
      self.advanceTime()
      print(self.time)
      yield

# multicore chip class
#   the workhorse that splits the load
class MultiCoreProcessor(CoroutineType):
  def __init__(self, sys):
    self.sys = sys
    # list of processors in this multicore setup
    self.processors = [Processor(self, i) for i in range(0, NUMPROCESSORS)]
  def run(self):
    while(True):
      yield

# the processor class
class Processor(CoroutineType):
  def __init__(self, mcp, id):
    # id of the processor
    self.mcp = mcp
    self.id = id
    self.jobslist = deque()
  def run(self):
    while(True):
      yield

# the process class
class Process(CoroutineType):
  def __init__(self, pid, arrivalt, instr):
    self.pid = pid
    self.arrivalt = arrivalt
    self.instr = instr
    self.totalTime = np.sum(instr, axis=0)
    self.totalPTime = np.sum(instr[::2], axis=0)
    self.totalWTime = np.sum(instr[1::2], axis=0)
    self.index = 0
  def run(self):
    self.instr[index] -= TIMEQ

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
        self.jobslist.append(Process(line[0], line[1], np.fromiter((int(t) for t in line[2:]), dtype=np.int16)))
    f.close()
  def run(self):
    while(True):
      if(self.jobslist[0].arrivalt <= self.sys.clock.getT()):
        newjob = self.jobslist.popleft()
        self.sys.mcp.newProcess(newjob)
        print('admitted new job @ {:}'.format(self.sys.clockgetT()))
      yield

class System():
  def __init__(self):
    self.clock = Clock(self)
    self.jobs = Jobs(self)
    self.mcp = MultiCoreProcessor(self)
    self.tm = TaskManager()
    self.jobs.loadProcessesFromFile(FILEPATH)
  def start(self):
    # start all tasks
    self.tm.new(self.mcp)
    self.tm.new(self.jobs)
    self.tm.new(self.clock)
    self.tm.mainloop()

sys = System()
sys.start()
