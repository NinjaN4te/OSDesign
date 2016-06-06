# a coroutinetype
from abc import ABCMeta

# virtual subclasses that derive from this type/class
#   are used primarily for use in coroutines
class CoroutineType(metaclass=ABCMeta):
  # define the abstract property/attribute _task, which is a reference
  #   to the task which is executing a coroutine of the run() function
  #   in an instance of this coroutinetype class
  def get_task(self):
    return self._task
  def set_task(self, newtask):
    self._task = newtask
  #_task = property(get_task, set_task)

  @classmethod
  def __subclasshook__(cls, C):
    if cls is CoroutineType:
      # a class is a virtual subclass of CoroutineType if it contains a method
      #   'run()' in itself or any of its base classes
      if any('run' in B.__dict__ for B in C.__mro__):
        return True
    return NotImplemented
