"""Targeted tests for ProcessRunner signal handling and interruption cleanup."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from workflow_orchestrator.agent_run_store import AgentRunStore
from workflow_orchestrator.process_runner import ProcessRunner, ProcessOutcome


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _make_store(tmp_path: Path) -> AgentRunStore:
    """Create an AgentRunStore in a temp directory."""
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    store = AgentRunStore(runtime, "BATCH-SIG-TEST", "TASK-SIG")
    store.acquire()
    return store


def _read_process_json(store: AgentRunStore) -> dict[str, Any]:
    path = store.run_dir / "process.json"
    return json.loads(path.read_text(encoding="utf-8"))


# --- Fake agent scripts ---

SLEEPER_SCRIPT = """\
import time, sys
time.sleep(60)
"""

QUICK_SCRIPT = """\
import sys
print("done")
sys.exit(0)
"""

IGNORANT_SCRIPT = """\
import signal, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
time.sleep(60)
"""


class TestProcessRunnerInterruption:
    """Tests for SIGINT/KeyboardInterrupt handling during agent execution."""

    def test_keyboard_interrupt_terminates_child(self, tmp_path: Path):
        """Ctrl+C (KeyboardInterrupt) terminates the fake agent subprocess."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")
        command = [sys.executable, str(script)]

        # Send SIGINT to ourselves after a short delay via a timer thread
        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        outcome = runner.run(command, tmp_path, {}, 60, store)
        assert outcome.cancelled is True
        assert outcome.timeout is False

    def test_no_residual_child_after_interrupt(self, tmp_path: Path):
        """After interrupt, no residual fake agent process remains."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")
        command = [sys.executable, str(script)]

        import threading
        child_pid_holder: list[int] = []

        original_run = subprocess.Popen
        class TrackingPopen(original_run):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                child_pid_holder.append(self.pid)

        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        # Monkey-patch Popen temporarily
        import workflow_orchestrator.process_runner as pr_module
        old_popen = pr_module.subprocess.Popen
        pr_module.subprocess.Popen = TrackingPopen
        try:
            outcome = runner.run(command, tmp_path, {}, 60, store)
        finally:
            pr_module.subprocess.Popen = old_popen

        assert outcome.cancelled is True
        # Verify child is gone
        if child_pid_holder:
            pid = child_pid_holder[0]
            time.sleep(0.2)
            with pytest.raises(ProcessLookupError):
                os.kill(pid, 0)

    def test_process_json_not_running_after_interrupt(self, tmp_path: Path):
        """process.json must not remain status: running after interrupt."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        proc = _read_process_json(store)
        assert proc["status"] != "running"

    def test_process_json_records_cancelled(self, tmp_path: Path):
        """process.json records cancelled status and cancelled: true."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        proc = _read_process_json(store)
        assert proc["status"] == "cancelled"
        assert proc["cancelled"] is True
        assert proc["shell"] is False
        assert "pid" in proc
        assert "duration_seconds" in proc

    def test_active_lock_released_after_interrupt(self, tmp_path: Path):
        """The .active.lock is released by run_agent's finally block (simulated)."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        try:
            runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        finally:
            store.release()  # simulates run_agent's finally block
        assert not store.lock_path.exists()

    def test_sigterm_path_same_as_sigint(self, tmp_path: Path):
        """SIGTERM follows the same cancellation path as SIGINT."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigterm():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGTERM)
        timer = threading.Thread(target=send_sigterm, daemon=True)
        timer.start()

        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert outcome.cancelled is True
        proc = _read_process_json(store)
        assert proc["status"] == "cancelled"

    def test_normal_success_path_unaffected(self, tmp_path: Path):
        """Normal successful execution still works correctly."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "quick.py"
        script.write_text(QUICK_SCRIPT, encoding="utf-8")

        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert outcome.exit_code == 0
        assert outcome.cancelled is False
        assert outcome.timeout is False
        assert "done" in outcome.stdout
        proc = _read_process_json(store)
        assert proc["status"] == "finished"
        assert proc["cancelled"] is False

    def test_timeout_path_unaffected(self, tmp_path: Path):
        """Timeout path still works correctly."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=2)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 1, store)
        assert outcome.timeout is True
        assert outcome.cancelled is False
        proc = _read_process_json(store)
        assert proc["status"] == "finished"
        assert proc["timeout"] is True

    def test_grace_period_no_hard_kill(self, tmp_path: Path):
        """Child that exits within grace period does not get SIGKILL."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=5)
        # Script that exits quickly on SIGTERM
        script = tmp_path / "graceful.py"
        script.write_text(
            "import signal, sys, time\n"
            "def handler(s, f): sys.exit(42)\n"
            "signal.signal(signal.SIGTERM, handler)\n"
            "time.sleep(60)\n",
            encoding="utf-8",
        )

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert outcome.cancelled is True
        # Process exited with 42 (SIGTERM handler), not -9 (SIGKILL)
        assert outcome.exit_code == 42

    def test_ignorant_child_gets_hard_kill(self, tmp_path: Path):
        """Child that ignores SIGTERM gets SIGKILL after grace period."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=1)
        script = tmp_path / "ignorant.py"
        script.write_text(IGNORANT_SCRIPT, encoding="utf-8")

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert outcome.cancelled is True
        # SIGKILL results in -9
        assert outcome.exit_code == -9

    def test_other_process_not_affected(self, tmp_path: Path):
        """An independent process is not killed by our cancellation."""
        # Start an independent background process
        independent = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            start_new_session=True,
        )
        try:
            store = _make_store(tmp_path)
            runner = ProcessRunner(graceful_termination_seconds=3)
            script = tmp_path / "sleeper.py"
            script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

            import threading
            def send_sigint():
                time.sleep(0.3)
                os.kill(os.getpid(), signal.SIGINT)
            timer = threading.Thread(target=send_sigint, daemon=True)
            timer.start()

            outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
            assert outcome.cancelled is True
            # Independent process should still be alive
            assert independent.poll() is None
        finally:
            independent.kill()
            independent.wait()

    def test_child_already_exited_no_double_error(self, tmp_path: Path):
        """If child exits just as interrupt arrives, no secondary exception."""
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        # Script that exits very quickly
        script = tmp_path / "fast.py"
        script.write_text("import sys; sys.exit(0)\n", encoding="utf-8")

        # Send interrupt after process likely already exited
        import threading
        def send_sigint():
            time.sleep(0.5)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        # Should not raise - process exits before signal arrives
        outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        # Either it completed normally or was cancelled - both are safe
        assert outcome.exit_code is not None or outcome.cancelled


class TestSignalHandlerLifecycle:
    """Tests that the SIGTERM handler is properly installed and restored."""

    def test_handler_restored_after_normal_success(self, tmp_path: Path):
        """Original SIGTERM handler is restored after normal completion."""
        original = signal.getsignal(signal.SIGTERM)
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "quick.py"
        script.write_text(QUICK_SCRIPT, encoding="utf-8")

        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert signal.getsignal(signal.SIGTERM) is original

    def test_handler_restored_after_timeout(self, tmp_path: Path):
        """Original SIGTERM handler is restored after timeout."""
        original = signal.getsignal(signal.SIGTERM)
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=1)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        runner.run([sys.executable, str(script)], tmp_path, {}, 1, store)
        assert signal.getsignal(signal.SIGTERM) is original

    def test_handler_restored_after_keyboard_interrupt(self, tmp_path: Path):
        """Original SIGTERM handler is restored after KeyboardInterrupt."""
        original = signal.getsignal(signal.SIGTERM)
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigint():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGINT)
        timer = threading.Thread(target=send_sigint, daemon=True)
        timer.start()

        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert signal.getsignal(signal.SIGTERM) is original

    def test_handler_restored_after_sigterm(self, tmp_path: Path):
        """Original SIGTERM handler is restored after SIGTERM cancellation."""
        original = signal.getsignal(signal.SIGTERM)
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "sleeper.py"
        script.write_text(SLEEPER_SCRIPT, encoding="utf-8")

        import threading
        def send_sigterm():
            time.sleep(0.3)
            os.kill(os.getpid(), signal.SIGTERM)
        timer = threading.Thread(target=send_sigterm, daemon=True)
        timer.start()

        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
        assert signal.getsignal(signal.SIGTERM) is original

    def test_consecutive_runs_no_handler_pollution(self, tmp_path: Path):
        """Second run does not inherit first run's temporary handler."""
        original = signal.getsignal(signal.SIGTERM)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "quick.py"
        script.write_text(QUICK_SCRIPT, encoding="utf-8")

        # First run
        store1 = _make_store(tmp_path)
        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store1)
        assert signal.getsignal(signal.SIGTERM) is original

        # Second run
        runtime2 = tmp_path / "runtime2"
        runtime2.mkdir()
        store2 = AgentRunStore(runtime2, "BATCH-SIG-TEST2", "TASK-SIG2")
        store2.acquire()
        runner.run([sys.executable, str(script)], tmp_path, {}, 60, store2)
        assert signal.getsignal(signal.SIGTERM) is original

    def test_background_thread_does_not_modify_handler(self, tmp_path: Path):
        """Running in a background thread does not install/modify signal handler."""
        import threading
        original = signal.getsignal(signal.SIGTERM)
        store = _make_store(tmp_path)
        runner = ProcessRunner(graceful_termination_seconds=3)
        script = tmp_path / "quick.py"
        script.write_text(QUICK_SCRIPT, encoding="utf-8")

        result_holder: list[ProcessOutcome] = []
        def run_in_thread():
            outcome = runner.run([sys.executable, str(script)], tmp_path, {}, 60, store)
            result_holder.append(outcome)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=10)
        assert len(result_holder) == 1
        assert result_holder[0].exit_code == 0
        # Handler must remain unchanged
        assert signal.getsignal(signal.SIGTERM) is original
