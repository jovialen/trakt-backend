import asyncio

import pytest

from trakt_backend.jobs import Job, QueueManager


@pytest.fixture
def jobs():
    return QueueManager(worker_count=1)


class SyncJob(Job):
    def __init__(self):
        self.executed = False

    def execute(self):
        self.executed = True


class AsyncJob(Job):
    def __init__(self):
        self.executed = asyncio.Event()

    async def execute(self):
        self.executed.set()


class FailingJob(Job):
    def execute(self):
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_queue_manager_executes_sync_job():
    manager = QueueManager(worker_count=1)
    manager.start()

    job = SyncJob()

    await manager.add(job)
    await manager.queue.join()

    assert job.executed

    await manager.stop()


@pytest.mark.asyncio
async def test_queue_manager_executes_async_job():
    manager = QueueManager(worker_count=1)
    manager.start()

    job = AsyncJob()

    await manager.add(job)
    await manager.queue.join()

    assert job.executed.is_set()

    await manager.stop()


@pytest.mark.asyncio
async def test_worker_continues_after_job_failure():
    manager = QueueManager(worker_count=1)
    manager.start()

    good = SyncJob()

    await manager.add(FailingJob())
    await manager.add(good)

    await manager.queue.join()

    assert good.executed

    await manager.stop()


@pytest.mark.asyncio
async def test_add_enqueues_job():
    manager = QueueManager(worker_count=0)

    job = SyncJob()

    await manager.add(job)

    assert manager.queue.qsize() == 1


@pytest.mark.asyncio
async def test_start_creates_requested_number_of_workers():
    manager = QueueManager(worker_count=3)

    manager.start()

    assert len(manager.workers) == 3
    assert all(not worker.done() for worker in manager.workers)

    await manager.stop()


@pytest.mark.asyncio
async def test_stop_cancels_workers():
    manager = QueueManager(worker_count=2)

    manager.start()
    workers = list(manager.workers)

    await manager.stop()

    assert all(worker.cancelled() or worker.done() for worker in workers)
