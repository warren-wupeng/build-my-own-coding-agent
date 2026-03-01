"""Heartbeat - Periodic tick driver for agent autonomy (Issue #3)

Each tick executes a fixed sequence:
    1. git pull (sync shared state)
    2. check_mailbox (read new messages)
    3. check_tasks (review assigned issues)
    4. execute_sop (run current SOP step)
    5. push_progress (commit & push changes)

The heartbeat runs in a loop with configurable interval, and can be
started/stopped programmatically.
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class TickResult:
    """Result of a single heartbeat tick."""
    tick_number: int
    timestamp: float
    steps_completed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class Heartbeat:
    """Configurable periodic trigger for agent autonomy.

    Each tick runs the full cycle: pull -> mailbox -> tasks -> sop -> push.
    Callbacks are registered for each step, allowing agents to define
    their own behavior at each stage.
    """

    def __init__(self, interval: float = 30.0, agent_name: str = "agent"):
        """Initialize heartbeat.

        Args:
            interval: Seconds between ticks (default 30s)
            agent_name: Name of the agent this heartbeat belongs to
        """
        self.interval = interval
        self.agent_name = agent_name

        # Step callbacks - each returns Optional[str] error message (None = success)
        self._steps: dict[str, Optional[Callable[[], Optional[str]]]] = {
            "git_pull": None,
            "check_mailbox": None,
            "check_tasks": None,
            "execute_sop": None,
            "push_progress": None,
        }

        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._tick_count = 0
        self._history: list[TickResult] = []
        self._stop_event = threading.Event()

    def register_step(self, step_name: str, callback: Callable[[], Optional[str]]):
        """Register a callback for a heartbeat step.

        Args:
            step_name: One of: git_pull, check_mailbox, check_tasks, execute_sop, push_progress
            callback: Function that returns None on success or error string on failure
        """
        if step_name not in self._steps:
            raise ValueError(
                f"Unknown step: {step_name}. "
                f"Valid steps: {list(self._steps.keys())}"
            )
        self._steps[step_name] = callback

    def tick(self) -> TickResult:
        """Execute one heartbeat cycle synchronously.

        Returns:
            TickResult with step outcomes
        """
        self._tick_count += 1
        result = TickResult(
            tick_number=self._tick_count,
            timestamp=time.time(),
        )

        for step_name, callback in self._steps.items():
            if callback is None:
                logger.debug(f"[{self.agent_name}] Skipping {step_name} (no callback)")
                continue

            try:
                error = callback()
                if error:
                    result.errors.append(f"{step_name}: {error}")
                    logger.warning(f"[{self.agent_name}] {step_name} failed: {error}")
                else:
                    result.steps_completed.append(step_name)
                    logger.debug(f"[{self.agent_name}] {step_name} completed")
            except Exception as e:
                result.errors.append(f"{step_name}: {e}")
                logger.error(f"[{self.agent_name}] {step_name} exception: {e}")

        self._history.append(result)
        return result

    def start(self):
        """Start the heartbeat loop in a background thread."""
        if self._running:
            logger.warning(f"[{self.agent_name}] Heartbeat already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name=f"heartbeat-{self.agent_name}",
            daemon=True,
        )
        self._thread.start()
        logger.info(f"[{self.agent_name}] Heartbeat started (interval={self.interval}s)")

    def stop(self):
        """Stop the heartbeat loop."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.interval + 5)
        logger.info(f"[{self.agent_name}] Heartbeat stopped after {self._tick_count} ticks")

    def _run_loop(self):
        """Internal loop that runs ticks at the configured interval."""
        while self._running:
            try:
                self.tick()
            except Exception as e:
                logger.error(f"[{self.agent_name}] Tick failed: {e}")

            # Wait for interval or stop signal
            if self._stop_event.wait(timeout=self.interval):
                break

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def tick_count(self) -> int:
        return self._tick_count

    @property
    def history(self) -> list[TickResult]:
        return list(self._history)

    @property
    def last_tick(self) -> Optional[TickResult]:
        return self._history[-1] if self._history else None
