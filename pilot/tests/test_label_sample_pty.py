"""PTY regression test for the optional note on the interactive ``f`` path."""
import json
import os
import pty
import select
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULE_DIR = os.path.join(ROOT, "pilot")


DRIVER = r'''
import json
import tempfile
from pathlib import Path
import label_sample

with tempfile.TemporaryDirectory() as directory:
    label_sample.LABELS = Path(directory) / 'labels.jsonl'
    for idx in range(2):
        label, note = label_sample.prompt_label({}, idx, {})
        label_sample.write_label(idx, 'tool', 'repo', [], label, note)
    labels = label_sample.load_labels()
    results = [[labels[str(idx)]['label'], labels[str(idx)]['note']]
               for idx in range(2)]
print("RESULT=" + json.dumps(results), flush=True)
'''


def _read_until(fd, output, predicate):
    deadline = time.time() + 5
    while time.time() < deadline:
        if predicate(output):
            return
        ready, _, _ = select.select([fd], [], [], 0.1)
        if not ready:
            continue
        try:
            chunk = os.read(fd, 4096)
        except OSError:
            return
        if not chunk:
            return
        output.extend(chunk)
    assert predicate(output), output.decode(errors="replace")


def main():
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(MODULE_DIR)
        os.execve(sys.executable, [sys.executable, "-c", DRIVER], os.environ.copy())
    output = bytearray()
    try:
        os.write(fd, b"f\n")
        _read_until(fd, output, lambda out: b"optional, Enter to skip" in out)
        os.write(fd, b"first pasted line\nsecond pasted line\n")
        _read_until(fd, output, lambda out: out.count(b"t/f/u/s/q > ") >= 2)
        os.write(fd, b"f\n")
        _read_until(fd, output, lambda out: out.count(b"optional, Enter to skip") >= 2)
        os.write(fd, b"\n")
        _read_until(fd, output, lambda out: b"RESULT=" in out and out.endswith(b"\n"))
    finally:
        os.close(fd)
        waited, status = os.waitpid(pid, os.WNOHANG)
        if not waited:
            os.kill(pid, 9)
            os.waitpid(pid, 0)
    text = output.decode(errors="replace")
    marker = "RESULT="
    assert marker in text, text
    results = json.loads(text.split(marker, 1)[1].splitlines()[0])
    assert results == [["fp", "first pasted line second pasted line"], ["fp", ""]], results
    assert "NOTE REQUIRED" not in text, text
    print("PTY optional-f-note branches: PASS")


if __name__ == "__main__":
    main()
