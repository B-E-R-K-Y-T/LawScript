from typing import Optional
import time

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='временная_метка')
class Time(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number

        return Number(time.time())


@builder.collect(func_name='спать')
class Sleep(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number, Void
        from core.exceptions import ErrorType

        if not isinstance(args[0], Number):
            raise ErrorType('Первый аргумент должен быть числом')

        time.sleep(args[0].value)

        return Void()


@builder.collect(func_name='спать_в_фоне')
class BackgroundSleep(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from threading import Lock
        from core.types.atomic import Number, Void, Yield, BaseAtomicType
        from core.exceptions import ErrorType
        from core.background_task.task import AbstractBackgroundTask

        if not isinstance(args[0], Number):
            raise ErrorType('Первый аргумент должен быть числом')

        class SleepTask(AbstractBackgroundTask):
            def __init__(self):
                self.sleep_time = args[0].value
                self._result = Void()
                self._done = False
                self._lock = Lock()
                self._gen_sleep = self.sleep()
                super().__init__(SleepTask.__name__, self.sleep_time)

            def sleep(self):
                start_time = time.time()

                while time.time() - start_time < self.sleep_time:
                   yield Yield()

            def next_command(self):
                try:
                    yield next(self._gen_sleep)
                except StopIteration as e:
                    self._result = e.value
                    return

            @property
            def done(self):
                return self._done

            @done.setter
            def done(self, value: bool):
                with self._lock:
                    self._done = value

            @property
            def result(self):
                return self._result

            @result.setter
            def result(self, value: BaseAtomicType):
                with self._lock:
                    self._result = value

        return SleepTask()


if __name__ == '__main__':
    builder.build_python_extend("время")
