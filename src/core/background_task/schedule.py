import atexit
import time
from itertools import cycle
from threading import Lock, Thread, Event
from typing import Optional

from config import settings
from src.core.background_task.task import AbstractBackgroundTask
from src.core.exceptions import BaseError, create_law_script_exception_class_instance
from src.core.types.atomic import Void
from src.util.console_worker import printer


class ThreadWorker:
    def __init__(self):
        self.thread: Optional[Thread] = None
        self.tasks: list[AbstractBackgroundTask] = []
        self._stop_event = Event()
        self._lock = Lock()
        self._task_added_event = Event()
        self._start_time = time.time()
        self._is_active = True

    def add_task(self, task: AbstractBackgroundTask):
        with self._lock:
            self.tasks.append(task)

    def start(self):
        self.thread = Thread(target=self._work, daemon=True)
        self.thread.start()
        printer.logging(f"{self.thread=} Запущен")

    def stop(self):
        self._stop_event.set()
        self._task_added_event.set()

        warn = ""

        for offset, task in enumerate(self.tasks):
            warn += f"Задача [{task.id}] '{task.name}' не была завершена корректно!\n"

        if warn:
            printer.print_warning(warn.rstrip(), self.thread.name)

        if self.thread:
            self.thread.join(timeout=1.0)

    def is_active(self):
        return self._is_active

    def done_task(self, task: AbstractBackgroundTask, task_id: int):
        with self._lock:
            task.done = True
            self.tasks.pop(task_id)

    def _work(self):
        while not self._stop_event.is_set():
            current_time = time.time()
            elapsed = current_time - self._start_time

            if not self.tasks and elapsed > settings.ttl_thread:
                with self._lock:
                    self._is_active = False
                self._stop_event.set()
                printer.logging(
                    f"{self.thread=} Нет задач, работа завершена по таймауту: {settings.ttl_thread}"
                )
                break

            if len(self.tasks) == 0:
                self._task_added_event.wait(timeout=settings.wait_task_time)
                self._task_added_event.clear()
                continue

            self._start_time = time.time()

            for idx, task in enumerate(self.tasks):
                try:
                    next(task.next_command())
                except StopIteration:
                    from src.core.executors.body import Stop

                    if isinstance(task.result, Stop):
                        task.result = Void()

                    self.done_task(task, idx)
                except BaseError as e:
                    task.result = create_law_script_exception_class_instance(e.exc_name, e)
                    task.is_error_result = True
                    task.error = e
                    self.done_task(task, idx)
                except Exception as e:
                    task.result = Void()
                    self.done_task(task, idx)

                    err_message = f"{self.thread.name}: Ошибка при выполнении задачи: [{idx}] '{task.name}'.\n\nДетали: {e}"

                    printer.print_error(err_message)


class TaskScheduler:
    def __init__(self):
        self.threads = []
        self._round_robin_process_list = None
        self._lock = Lock()
        atexit.register(self.shutdown)

    def shutdown(self):
        with self._lock:
            for worker in self.threads:
                worker.stop()
            self.threads.clear()

    def schedule_task(self, task: AbstractBackgroundTask):
        worker = self.next_worker()

        while not worker.is_active():
            worker = self.next_worker()

        worker.add_task(task)

    def next_worker(self) -> ThreadWorker:
        with self._lock:
            for idx, worker in enumerate(self.threads):
                if not worker.is_active():
                    self.threads.pop(idx)

            if len(self.threads) >= settings.max_running_threads_tasks:
                if self._round_robin_process_list is None:
                    self._round_robin_process_list = cycle(self.threads)

                return next(self._round_robin_process_list)

            worker = ThreadWorker()
            worker.start()
            self.threads.append(worker)
            self._round_robin_process_list = cycle(self.threads)

            return worker


def get_task_scheduler() -> TaskScheduler:
    """Лениво создаёт планировщик задач при первом вызове."""
    if not hasattr(get_task_scheduler, '_instance'):
        get_task_scheduler._instance = TaskScheduler()

    return get_task_scheduler._instance
