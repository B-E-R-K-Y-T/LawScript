from itertools import cycle
from multiprocessing import Queue as ProcessQueue, Process
from threading import Lock, Thread, Event
from typing import Optional

from config import settings
from core.exceptions import MaxThreadsError


class RoundRobinTaskList:
    def __init__(self, max_len: int = settings.max_tasks_in_thread):
        self.items = []
        self.max_len = max_len
        self.cycled_items = cycle(self.items)
        self._lock = Lock()

    def append(self, item):
        if self.is_full():
            raise MaxThreadsError

        with self._lock:
            self.items.append(item)

    def get_task(self, index: int):
        return self.items[index]

    def is_full(self):
        if self.max_len == -1:
            return False

        return len(self.items) >= self.max_len

    def __iter__(self):
        return self.cycled_items


class ThreadWorker:
    def __init__(self):
        self.thread = None
        self.tasks = RoundRobinTaskList()
        self.max_tasks_in_thread = settings.max_tasks_in_thread
        self._stop_event = Event()
        self._task_added_event = Event()

    def add_task(self, task):
        while self.tasks.is_full() and not self._stop_event.is_set():
            self._task_added_event.wait(timeout=0.1)
            self._task_added_event.clear()

        if self._stop_event.is_set():
            raise RuntimeError("ThreadWorker is stopping")

        self.tasks.append(task)

    def start(self):
        self.thread = Thread(target=self._work)
        self.thread.daemon = True
        self.thread.start()

    def _work(self): ...


class ProcessWorker:
    def __init__(self):
        self.process: Optional[Process] = None
        self.threads = []
        self.max_processes = settings.max_process_threads
        self.tasks_queue = ProcessQueue()
        self._round_robin_thread = None

    def run_task(self, task):
        self.tasks_queue.put(task)

    def start(self):
        self.process = Process(target=self._work)

    def next_thread(self) -> ThreadWorker:
        if len(self.threads) >= self.max_processes:
            if self._round_robin_thread is None:
                self._round_robin_thread = cycle(self.threads)

            return next(self._round_robin_thread)

        thread = ThreadWorker()
        self.threads.append(thread)

        return thread

    def _work(self):
        while True:
            task = self.tasks_queue.get()

            if task is None:
                continue

            self.next_thread().add_task(task)


class TaskScheduler:
    def __init__(self):
        self.processes = []
        self._round_robin_process_list = None

    def schedule_task(self, task):
        worker = self.next_worker()
        worker.run_task(task)

    def next_worker(self) -> ProcessWorker:
        if len(self.processes) >= settings.max_background_processes:
            if self._round_robin_process_list is None:
                self._round_robin_process_list = cycle(self.processes)

            return next(self._round_robin_process_list)

        worker = ProcessWorker()
        worker.start()
        self.processes.append(worker)

        return worker


task_scheduler = TaskScheduler()
