"""
Productivity plugin for Buddy.

Mimics the feature-set of common productivity / todo apps:
  - Adding, listing, completing, and clearing todo items
  - Setting simple reminders (backed by the Scheduler)
  - Managing a basic workflow queue

Register with the TaskEngine via ``register(engine)``.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TodoList:
    """In-memory todo list manager.

    Attributes:
        _items: Ordered list of item dicts with keys
                ``id``, ``text``, ``done``, ``created_at``.
    """

    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []
        self._next_id: int = 1

    def add(self, text: str) -> Dict[str, Any]:
        """Add a new todo *text* and return the created item dict."""
        item = {
            "id": self._next_id,
            "text": text,
            "done": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._items.append(item)
        self._next_id += 1
        logger.info("Todo added: %r (id=%d)", text, item["id"])
        return item

    def list_items(self, show_done: bool = True) -> List[Dict[str, Any]]:
        """Return all items, optionally filtering out completed ones."""
        if show_done:
            return list(self._items)
        return [i for i in self._items if not i["done"]]

    def complete(self, identifier: Any) -> Optional[Dict[str, Any]]:
        """Mark a todo item as done by *identifier* (id or text substring).

        Args:
            identifier: Integer ID or partial text string.

        Returns:
            The updated item dict, or ``None`` if not found.
        """
        for item in self._items:
            match = (
                (isinstance(identifier, int) and item["id"] == identifier)
                or (
                    isinstance(identifier, str)
                    and identifier.lower() in item["text"].lower()
                )
            )
            if match and not item["done"]:
                item["done"] = True
                logger.info("Todo completed: %r (id=%d)", item["text"], item["id"])
                return item
        return None

    def clear(self, done_only: bool = False) -> int:
        """Remove items. Returns number removed.

        Args:
            done_only: If ``True`` only remove completed items.
        """
        before = len(self._items)
        if done_only:
            self._items = [i for i in self._items if not i["done"]]
        else:
            self._items.clear()
        removed = before - len(self._items)
        logger.info("Cleared %d todo items.", removed)
        return removed


class WorkflowQueue:
    """Simple FIFO workflow step queue."""

    def __init__(self) -> None:
        self._steps: List[str] = []

    def enqueue(self, step: str) -> None:
        """Add a workflow step to the end of the queue."""
        self._steps.append(step)

    def dequeue(self) -> Optional[str]:
        """Remove and return the next workflow step, or ``None``."""
        return self._steps.pop(0) if self._steps else None

    def peek(self) -> Optional[str]:
        """Return the next step without removing it."""
        return self._steps[0] if self._steps else None

    def all_steps(self) -> List[str]:
        """Return all pending steps."""
        return list(self._steps)

    def clear(self) -> None:
        """Remove all pending steps."""
        self._steps.clear()


# ---------------------------------------------------------------------------
# Task handlers – called by the TaskEngine
# ---------------------------------------------------------------------------

_todo_list = TodoList()
_workflow_queue = WorkflowQueue()


def handle_add_todo(params: Dict[str, Any]) -> Dict[str, Any]:
    item_text = params.get("item", "").strip()
    if not item_text:
        return {"success": False, "message": "No todo text provided."}
    item = _todo_list.add(item_text)
    return {"success": True, "message": f"Added: \"{item_text}\"", "item": item}


def handle_list_todos(params: Dict[str, Any]) -> Dict[str, Any]:
    items = _todo_list.list_items()
    if not items:
        return {"success": True, "message": "Your todo list is empty.", "items": []}
    lines = [
        f"[{'x' if i['done'] else ' '}] {i['id']}. {i['text']}" for i in items
    ]
    return {
        "success": True,
        "message": "\n".join(lines),
        "items": items,
    }


def handle_complete_todo(params: Dict[str, Any]) -> Dict[str, Any]:
    identifier = params.get("item", "").strip()
    # Try numeric ID first
    try:
        identifier = int(identifier)
    except (ValueError, TypeError):
        pass
    item = _todo_list.complete(identifier)
    if item is None:
        return {
            "success": False,
            "message": f"No pending todo matching \"{identifier}\".",
        }
    return {"success": True, "message": f"Completed: \"{item['text']}\"", "item": item}


def handle_schedule_task(params: Dict[str, Any], scheduler: Any = None) -> Dict[str, Any]:
    task_name = params.get("task", "unnamed task")
    when = params.get("when", "")

    if scheduler is not None:
        task_id = scheduler.schedule_task(
            name=task_name,
            callback=lambda: logger.info("Scheduled task fired: %s", task_name),
            delay=0,
        )
        return {
            "success": True,
            "message": f"Scheduled \"{task_name}\" for {when or 'now'}.",
            "task_id": task_id,
        }
    return {
        "success": True,
        "message": f"Task \"{task_name}\" noted for {when or 'now'} (no scheduler attached).",
    }


def handle_set_reminder(params: Dict[str, Any], scheduler: Any = None) -> Dict[str, Any]:
    message = params.get("message", "reminder")
    when = params.get("when", "")
    full_message = f"Reminder: {message}"

    if scheduler is not None:
        task_id = scheduler.schedule_task(
            name=full_message,
            callback=lambda: logger.info("Reminder fired: %s", message),
            delay=0,
        )
        return {
            "success": True,
            "message": f"Reminder set: \"{message}\" at {when or 'next available time'}.",
            "task_id": task_id,
        }
    return {
        "success": True,
        "message": f"Reminder noted: \"{message}\" for {when or 'unspecified time'}.",
    }


def handle_enqueue_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    step = params.get("step", "").strip()
    if not step:
        return {"success": False, "message": "No workflow step provided."}
    _workflow_queue.enqueue(step)
    return {
        "success": True,
        "message": f"Workflow step enqueued: \"{step}\".",
        "queue": _workflow_queue.all_steps(),
    }


def handle_show_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    steps = _workflow_queue.all_steps()
    if not steps:
        return {"success": True, "message": "Workflow queue is empty.", "steps": []}
    return {
        "success": True,
        "message": "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)),
        "steps": steps,
    }


def handle_help(params: Dict[str, Any]) -> Dict[str, Any]:
    help_text = (
        "Here is what I can do:\n"
        "  • add [task/todo/item] <text>        – Add a todo item\n"
        "  • list [tasks/todos/items]            – Show your todo list\n"
        "  • complete/done <text or id>          – Mark a todo as done\n"
        "  • schedule <task> at/on/for <when>    – Schedule a task\n"
        "  • remind me to <message> at <when>    – Set a reminder\n"
        "  • fetch <url>                         – Fetch data from a URL\n"
        "  • search for <query>                  – Search the web\n"
        "  • install library <package>           – Install a Python package\n"
        "  • benchmark <target>                  – Run a benchmark\n"
        "  • help                                – Show this help message\n"
    )
    return {"success": True, "message": help_text}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(engine: Any, scheduler: Any = None) -> None:
    """Register productivity capabilities with *engine*.

    Args:
        engine: :class:`~BuddyAI.task_engine.TaskEngine` instance.
        scheduler: Optional :class:`~BuddyAI.scheduler.Scheduler` instance
                   for time-based tasks.
    """
    import functools

    engine.register_capability("add_todo", handle_add_todo)
    engine.register_capability("list_todos", handle_list_todos)
    engine.register_capability("complete_todo", handle_complete_todo)
    engine.register_capability("help", handle_help)

    # Inject scheduler into handlers that need it
    engine.register_capability(
        "schedule_task",
        functools.partial(handle_schedule_task, scheduler=scheduler),
    )
    engine.register_capability(
        "set_reminder",
        functools.partial(handle_set_reminder, scheduler=scheduler),
    )
    engine.register_capability("enqueue_workflow", handle_enqueue_workflow)
    engine.register_capability("show_workflow", handle_show_workflow)

    logger.info("Productivity plugin registered.")
