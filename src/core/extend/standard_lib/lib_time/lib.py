from typing import Optional
import time

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "время"


@builder.collect(func_name='временная_метка')
class Time(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import time
        from src.core.types.atomic import Number

        return Number(time.time())


@builder.collect(func_name='спать')
class Sleep(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import time
        from src.core.types.atomic import Number, VOID
        from src.core.exceptions import ErrorType

        if not isinstance(args[0], Number):
            raise ErrorType('Первый аргумент должен быть числом')

        time.sleep(args[0].value)

        return VOID


@builder.collect(func_name='асинхронный_сон')
class BackgroundSleep(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from threading import Lock
        from src.core.types.atomic import Number, VOID, YIELD, BaseAtomicType
        from src.core.exceptions import ErrorType
        from src.core.background_task.task import AbstractBackgroundTask

        if not isinstance(args[0], Number):
            raise ErrorType('Первый аргумент должен быть числом')

        name = self.func_name

        class SleepTask(AbstractBackgroundTask):
            def __init__(self):
                self.sleep_time = args[0].value
                self._result = VOID
                self._done = False
                self._lock = Lock()
                self._gen_sleep = self.sleep()
                self._delta_sleep_time = 0.0001
                self._switch_point = 100
                super().__init__(name, self.sleep_time)

            def sleep(self):
                start_time = time.monotonic()
                switch = 0

                while time.monotonic() - start_time < self.sleep_time:
                    if switch >= self._switch_point:
                        time.sleep(self._delta_sleep_time)
                        switch = 0

                    yield YIELD

                return VOID

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


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
