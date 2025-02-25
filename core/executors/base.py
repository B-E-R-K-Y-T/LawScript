from abc import ABC, abstractmethod

from core.types.basetype import BaseAtomicType


class Executor(ABC):
    @abstractmethod
    def execute(self) -> BaseAtomicType: ...
