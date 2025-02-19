import heapq
from threading import Lock


class Scheduler:
    def __init__(self, available_tasks):
        self._available_tasks = available_tasks
        self._lock = Lock()
        self._tasks = set()
        self._queue = list()

    def add_task(self, task, timestamp):
        with self._lock:
            if task not in self._available_tasks:
                # Do not allow
                return

            if task in self._tasks:
                # No re-scheduling available
                return

            self._tasks.add(task)
            heapq.heappush(self._queue, (timestamp, task))

    def get_awaiting(self, timestamp):
        result = []

        with self._lock:
            while self._queue and self._queue[0][0] < timestamp:
                head = heapq.heappop(self._queue)
                self._tasks.remove(head[1])
                result.append(head[1])

        return result
