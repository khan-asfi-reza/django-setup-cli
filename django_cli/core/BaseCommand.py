import abc
from dataclasses import dataclass
from typing import Callable, List


def register(foreign_decorator: Callable) -> Callable:
    """
    Returns a copy of foreignDecorator, which is identical in every
    way(*), except also appends a .decorator property to the callable it
    spits out.
    :keyword foreign_decorator
    :param foreign_decorator:Callable
    :return: Callable
    """

    def decorator_factory(*args, **kwargs) -> Callable:
        old_generated_decorator = foreign_decorator(*args, **kwargs)

        def generated_decorator(func):
            modified = old_generated_decorator(func)
            modified.decorator = decorator_factory
            return modified

        return generated_decorator

    decorator_factory.__name__ = foreign_decorator.__name__
    decorator_factory.__doc__ = foreign_decorator.__doc__
    return decorator_factory


@dataclass
class TaskQueue:
    """
    Stores functions/callables in a queue and executes them serially
    :arg
        queue (list[Callable]): Function Queue
    """
    queue: List[Callable]

    def dequeue(self, *args, **kwargs) -> None:
        self.queue.pop()(*args, **kwargs)

    def execute(self, *args, **kwargs):
        for q in self.queue:
            self.dequeue(*args, **kwargs)


def pre_execute(*args, **kwargs) -> Callable:
    """
    Enquire From User decorator
    :return: Callable
    """

    def wrapper(func: Callable) -> Callable:
        return func

    return wrapper


pre_execute = register(pre_execute)


class BaseCommand(abc.ABC):

    @classmethod
    def method_with_decorator(cls, decorator):
        """
            Returns all methods in CLS with DECORATOR as the
            outermost decorator.

            DECORATOR must be a "registering decorator"; one
            can make any decorator "registering" via the
            makeRegisteringDecorator function.
        """
        for maybeDecorated in cls.__dict__.values():
            if hasattr(maybeDecorated, 'decorator'):
                if maybeDecorated.decorator == decorator:
                    yield maybeDecorated

    def execute_tasks(self):
        """
        Executes all task methods,
        Take input from User, store them
        And execute
        :return:
        """
        TaskQueue(list(self.method_with_decorator(pre_execute))).execute(self)

    @staticmethod
    def execute(task):
        def wrapper(self, *args, **kwargs):
            self.execute_tasks()
            task(self, *args, **kwargs)

        return wrapper
