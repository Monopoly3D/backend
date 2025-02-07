import asyncio
from asyncio import Task
from typing import List


def get_task(name: str) -> Task | None:
    tasks: List[Task] = [task for task in asyncio.all_tasks() if task.get_name() == name]

    if not tasks:
        return

    return tasks[0]
