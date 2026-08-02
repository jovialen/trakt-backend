import asyncio
import inspect
from logging import debug, exception
from typing import Annotated

from fastapi import Depends


class Job:
    def execute(self):
        pass


async def job_worker(queue: asyncio.Queue[Job]):
    debug("Worker started watching queue %s", hex(id(queue)))
    while True:
        job = await queue.get()
        debug("Starting job")
        try:
            result = job.execute()
            if inspect.isawaitable(result):
                await result
        except Exception:
            exception("Job failed")
        finally:
            queue.task_done()


class QueueManager:
    def __init__(self, worker_count: int = 10):
        self.queue = asyncio.Queue[Job]()
        self.worker_count = worker_count
        self.workers = []

    async def add(self, job: Job):
        debug("Enqueueing job in %s", hex(id(self.queue)))
        await self.queue.put(job)

    def start(self):
        self.workers = [
            asyncio.create_task(job_worker(self.queue)) for _ in range(self.worker_count)
        ]

    async def stop(self):
        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)


jobs = QueueManager()


def get_jobs():
    return jobs


JobsDep = Annotated[QueueManager, Depends(get_jobs)]
