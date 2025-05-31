from core.executors.body import BodyExecutor


class BackgroundTask:
    def __init__(self, executor: BodyExecutor):
        self.executor = executor
        self._generator = executor.execute()

    def result(self):
        return None

    def next_command(self):
        return next(self._generator)
