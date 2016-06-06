# ----------------------------------------------------------------------- #
# TASKMANAGER
# ----------------------------------------------------------------------- #
# module to contain class that wraps a coroutine, called Task
# also the main manager that manages them (danmakufu-like)
# Code referenced from:
#   www.dabeaz.com/coroutines/Coroutines.pdf

# LIBRARIES
# ----------------------------------------- #
from collections import deque

# user libraries/scripts




# TASK OBJECT
# ----------------------------------------------------------------------- #
# wraps a coroutine
# simply call the run() member function
# target param accepts a coroutine function that contains yields
#   eg: t1 = Task(foo()); t1.run(),  where foo() contains yields here and there
#   run() executes the task to the next yield
class Task(object):
  taskid = 0
  def __init__(self, target, tm):
    Task.taskid += 1
    self.tid      = Task.taskid   # Task ID
    self.target   = target        # Target coroutine
    self.sendval  = None          # Value to send
    self.tm       = tm            # reference to task manager of this task
    self.children = deque()       # list of tasks spawned off of this task
  def run(self):
    return self.target.send(self.sendval)
  def new(self, target):
    # add new child task, if this parent task dies, all the children go with it
    child = self.tm.new(target, obj=True)
    self.children.append(child)
  def killChildren(self):
    for child in self.children:
      child.target.close()
# TASK MANAGER
# ----------------------------------------------------------------------- #
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
    task.killChildren()
    self.taskmap.pop(task.tid, 'None')
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

