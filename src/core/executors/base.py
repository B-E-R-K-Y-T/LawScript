from abc import ABC, abstractmethod

from src.core.types.basetype import BaseAtomicType


class Executor(ABC):
    @abstractmethod
    def execute(self) -> BaseAtomicType: ...
