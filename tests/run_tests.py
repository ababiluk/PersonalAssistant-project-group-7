"""
Run all tests and save output to a timestamped log file.
Appends a results summary table at the end of the log.

Usage:
    python tests/run_tests.py
"""
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_path = LOGS_DIR / f"test_run_{timestamp}.log"

# PYTHONIOENCODING=utf-8 forces pytest to write UTF-8 even on Windows cp1252 terminals
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

# ---------------------------------------------------------------------------
# Run pytest  (-r xf includes xfail + failed reasons in short test summary)
# ---------------------------------------------------------------------------
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-r", "xf"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    env=ENV,
)
output = result.stdout + result.stderr

# ---------------------------------------------------------------------------
# Parse short test summary  →  failed_rows / xfail_rows
# Format of each relevant line:
#   FAILED tests/file.py::Class::test_name - error message
#   XFAIL  tests/file.py::Class::test_name - reason text
# ---------------------------------------------------------------------------
failed_rows = []  # (short_file, cls, test, detail)
xfail_rows  = []

summary_section = re.search(
    r"={5,}\s*short test summary info\s*={5,}\n(.*?)(?:\n={5,}|\Z)",
    output,
    re.DOTALL,
)
if summary_section:
    for line in summary_section.group(1).splitlines():
        m = re.match(r"^(FAILED|ERROR|XFAIL)\s+(tests/.+?)\s+-\s+(.*)", line.strip())
        if not m:
            continue
        status, test_id, detail = m.groups()
        parts      = test_id.split("::")
        short_file = Path(parts[0]).name
        cls        = parts[1] if len(parts) > 1 else ""
        test       = parts[2] if len(parts) > 2 else ""
        row = (short_file, cls, test, detail.strip())
        if status in ("FAILED", "ERROR"):
            failed_rows.append(row)
        else:
            xfail_rows.append(row)

# ---------------------------------------------------------------------------
# Find fix location in source code
# Strategy (tried in order):
#   1. Extract method names from test_name and grep for "def <method>("
#   2. Extract class entity from test class name and grep for "class <Entity>("
# Source search paths: models/, handlers/, decorators/
# ---------------------------------------------------------------------------
SOURCE_DIRS = [ROOT / d for d in ("models", "handlers", "decorators")]


def _grep_source(pattern):
    """Return 'filename:line_number' for the first match of pattern in source dirs."""
    for d in SOURCE_DIRS:
        if not d.exists():
            continue
        for py in sorted(d.glob("*.py")):
            for i, line in enumerate(
                py.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if re.search(pattern, line):
                    return f"{py.name}:{i}"
    return None


def fix_location(cls_name, test_name):
    """
    Search production source code for the most relevant fix point.

    Priority:
      1. def <method>  extracted from test name (longest match first)
      2. class <Entity>  extracted from test class name
    """
    # Build candidate method names from test name
    # test_edit_note_preserves_tags  ->  ["edit_note_preserves", "edit_note", "edit"]
    raw = re.sub(r"^test_", "", test_name).split("_")
    method_candidates = [
        "_".join(raw[:n])
        for n in range(min(4, len(raw)), 1, -1)
    ]

    for method in method_candidates:
        loc = _grep_source(rf"def {re.escape(method)}\b")
        if loc:
            return loc

    # Extract class entity from test class name:
    # TestPhoneField -> Phone,  TestNoteCommands -> Note,  TestAddressBook -> AddressBook
    entity = re.sub(r"^Test|Field$|Commands?$", "", cls_name)
    if entity:
        loc = _grep_source(rf"class {re.escape(entity)}\b")
        if loc:
            return loc

    return "N/A"


# Attach fix locations to each row  →  (file, cls, test, detail, fix_loc)
def _enrich(rows):
    return [(*row, fix_location(row[1], row[2])) for row in rows]


failed_rows = _enrich(failed_rows)
xfail_rows  = _enrich(xfail_rows)

# ---------------------------------------------------------------------------
# Table renderer
# ---------------------------------------------------------------------------
def _table(headers, rows, max_detail=55):
    """Plain ASCII box table. 'detail' column capped at max_detail chars."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    widths[-2] = min(widths[-2], max_detail)   # detail/reason column  (second-to-last)

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    fmt = "|" + "|".join(f" {{:<{w}}} " for w in widths) + "|"

    lines = [sep, fmt.format(*headers), sep]
    for row in rows:
        cells = list(row)
        cells[-2] = str(cells[-2])[:widths[-2]]  # truncate detail column
        lines.append(fmt.format(*cells))
    lines.append(sep)
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Build summary
# ---------------------------------------------------------------------------
SEP = "=" * 72
lines = ["", SEP, "RESULTS SUMMARY", SEP, ""]

if failed_rows:
    lines += [
        f"  FAILED / ERROR : {len(failed_rows)}",
        "",
        _table(
            ["File", "Class", "Test", "Error", "Fix (file:line)"],
            failed_rows,
        ),
        "",
    ]
else:
    lines += ["  FAILED : 0  --  all tests passed", ""]

if xfail_rows:
    lines += [
        f"  XFAILED : {len(xfail_rows)}  (known bugs, expected to fail)",
        "",
        _table(
            ["File", "Class", "Test", "Reason", "Fix (file:line)"],
            xfail_rows,
        ),
        "",
    ]

summary = "\n".join(lines)

# ---------------------------------------------------------------------------
# Write log and print to console
# ---------------------------------------------------------------------------
log_path.write_text(output + summary, encoding="utf-8")

try:
    print(output, end="")
    print(summary)
except UnicodeEncodeError:
    safe = (output + summary).encode(
        sys.stdout.encoding or "ascii", errors="replace"
    ).decode(sys.stdout.encoding or "ascii")
    print(safe)

print(f"\nLog saved -> {log_path}")
sys.exit(result.returncode)
