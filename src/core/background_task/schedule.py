import atexit
import random
import time
from itertools import cycle
from threading import Lock, Thread, Event
from typing import Optional, Final, Generator

from config import settings
from src.core.background_task.task import AbstractBackgroundTask
from src.core.exceptions import BaseError, create_law_script_exception_class_instance
from src.core.types.atomic import VOID
from src.util.console_worker import printer

_GLOBAL_TASKS_LOCK: Final[Lock] = Lock()


class ThreadWorker:
    def __init__(self):
        self.thread: Optional[Thread] = None
        self.tasks: list[AbstractBackgroundTask] = []
        self._stop_event = Event()
        self.lock = Lock()
        self._task_added_event = Event()
        self._start_time = time.monotonic()
        self._is_active = True
        self._scheduler = get_task_scheduler()

    def add_task(self, task: AbstractBackgroundTask):
        with _GLOBAL_TASKS_LOCK:
            self.tasks.append(task)

    def start(self):
        self.thread = Thread(target=self._work, daemon=True)
        self.thread.start()
        printer.logging(f"{self.thread=} Запущен")

    def stop(self):
        self._stop_event.set()
        self._task_added_event.set()

        warn = ""

        for task in self.tasks:
            warn += f"Задача [{task.id}] '{task.name}' не была завершена корректно!\n"

        if warn:
            printer.print_warning(warn.rstrip(), self.thread.name)

        if self.thread:
            self.thread.join(timeout=settings.time_to_join_thread)

        printer.logging(f"{self.thread=} Остановлен")

    def is_active(self):
        return self._is_active

    def done_task(self, task: AbstractBackgroundTask):
        with _GLOBAL_TASKS_LOCK:
            task.done = True
            self.tasks.remove(task)

    def _work(self):
        while not self._stop_event.is_set():
            current_time = time.monotonic()
            elapsed = current_time - self._start_time

            if not self.tasks:
                printer.logging(f"{self.thread=} Голоден. Попытка получить задачу...")
                task = self._scheduler.get_free_task()

                if task is not None:
                    printer.logging(f"{self.thread=} Забрал задачу")
                    self.add_task(task)
                else:
                    time.sleep(settings.ttl_check_free_tasks)

            if not self.tasks and elapsed > settings.ttl_thread:
                with self.lock:
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

            self._start_time = time.monotonic()

            with _GLOBAL_TASKS_LOCK:
                task: AbstractBackgroundTask = random.choice(self.tasks)

            with task.exec_lock:
                try:
                    task.is_active = True
                    next(task.next_command())
                except StopIteration:
                    from src.core.executors.body import Stop

                    if isinstance(task.result, Stop):
                        task.result = VOID

                    self.done_task(task)
                except BaseError as e:
                    task.result = create_law_script_exception_class_instance(e.exc_name, e)
                    task.is_error_result = True
                    task.error = e
                    self.done_task(task)
                except Exception as e:
                    task.result = VOID
                    self.done_task(task)

                    err_message = (
                        f"{self.thread.name}: Ошибка при выполнении задачи: [{task.id}] '{task.name}'."
                        f"\n\nДетали: {e}"
                    )

                    printer.print_error(err_message)
                finally:
                    task.is_active = False


class TaskScheduler:
    def __init__(self):
        self.threads: list[ThreadWorker] = []
        self._round_robin_process_list: Optional[Generator[ThreadWorker]] = None
        self._lock = Lock()
        atexit.register(self.shutdown)

    def shutdown(self):
        with self._lock:
            for worker in self.threads:
                worker.stop()
            self.threads.clear()

    def get_free_task(self) -> Optional[AbstractBackgroundTask]:
        with self._lock:
            for worker in self.threads:
                if not worker.is_active():
                    continue

                if len(worker.tasks) > 1:
                    for idx, task in enumerate(worker.tasks):
                        if task.is_active:
                            continue

                        printer.logging(f"{worker.thread=} Отдал задачу")
                        return worker.tasks.pop(idx)

        return None

    def schedule_task(self, task: AbstractBackgroundTask):
        worker = self.next_worker()

        while not worker.is_active():
            worker = self.next_worker()

        worker.add_task(task)

    def next_worker(self) -> ThreadWorker:
        with self._lock:
            i = len(self.threads) - 1
            while i >= 0:
                if not self.threads[i].is_active():
                    self.threads.pop(i)
                i -= 1

            if self.threads and self._round_robin_process_list is not None:
                worker = next(self._round_robin_process_list)

                if len(worker.tasks) < settings.task_on_thread_step:
                    return worker

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
