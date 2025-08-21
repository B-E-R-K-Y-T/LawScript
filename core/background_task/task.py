from abc import ABC, abstractmethod
from threading import Lock
from typing import TYPE_CHECKING, Generator, Any

from core.types.basetype import BaseAtomicType

if TYPE_CHECKING:
    from core.executors.procedure import ProcedureExecutor


def _next_id():
    if not hasattr(_next_id, "current_id"):
        _next_id.current_id = -1

    _next_id.current_id += 1

    return _next_id.current_id


class AbstractBackgroundTask(BaseAtomicType, ABC):
    def __init__(self, name: str, value: Any):
        super().__init__(value)
        self.name = name
        self.id = _next_id()

    @abstractmethod
    def next_command(self): ...

    @abstractmethod
    def done(self): ...

    @abstractmethod
    def result(self): ...


class ProcedureBackgroundTask(AbstractBackgroundTask):
    def __init__(self,  name: str, executor: 'ProcedureExecutor'):
        super().__init__(name, executor)
        self.executor = executor
        self._generator = executor.async_execute()
        self._current_result = None
        self._done = False
        self._lock = Lock()

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, value: bool):
        with self._lock:
            self._done = value

    @property
    def result(self):
        return self._current_result

    @result.setter
    def result(self, value):
        with self._lock:
            self._current_result = value

    def next_command(self):
        try:
            self._current_result = next(self._generator)

            if not isinstance(self._current_result, Generator):
                yield self._current_result

            yield from self._current_result
        except StopIteration as e:
            self._current_result = e.value
            return

    def __repr__(self):
        return f'<ProcedureBackgroundTask name={str(self)} {self.executor=}, {self._current_result=}, {self._done=}>'
