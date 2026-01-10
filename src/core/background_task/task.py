from abc import ABC, abstractmethod
from threading import Lock
from typing import TYPE_CHECKING, Generator, Any, Optional

from src.core.types.basetype import BaseAtomicType

if TYPE_CHECKING:
    from src.core.executors.procedure import ProcedureExecutor
    from src.core.exceptions import BaseError


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
        self.is_error_result = False
        self._is_active = False
        self.error: Optional['BaseError'] = None
        self._waited_lock = Lock()
        self._lock = Lock()
        self.exec_lock = Lock()
        self._waited = False

    @property
    def is_active(self):
        with self._lock:
            return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        with self._lock:
            self._is_active = value

    def is_waited(self):
        return self._waited

    def set_waited(self):
        with self._waited_lock:
            self._waited = True

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
        self._procedure_lock = Lock()

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, value: bool):
        with self._procedure_lock:
            self._done = value

    @property
    def result(self):
        return self._current_result

    @result.setter
    def result(self, value):
        with self._procedure_lock:
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
