import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"

KNOWN_BUGS = {
    "test_add_contact_name_with_space": (
        "isalpha() rejects names with spaces (\"Mary Jane\" not accepted)",
        "handlers/contact_handlers.py:7",
    ),
    "test_birthdays_no_upcoming": (
        "birthdays() signature is (book) instead of (args, book)",
        "handlers/birthday_handlers.py:27",
    ),
    "test_birthdays_with_upcoming": (
        "birthdays() signature is (book) instead of (args, book)",
        "handlers/birthday_handlers.py:27",
    ),
    "test_birthday_impossible_date": (
        "Error message says 'Invalid date format' for impossible dates (e.g. 30.02)",
        "models/fields.py:28",
    ),
    "test_record_str_no_phones": (
        "Record.__str__ outputs 'phones: ' (empty) instead of 'phones: -'",
        "models/record.py:33",
    ),
    "test_unicode_digits": (
        "Phone accepts Unicode digits (Arabic etc.) — isdigit() returns True for non-ASCII",
        "models/fields.py:18",
    ),
    "test_no_leading_zero": (
        "Birthday('1.1.2000') accepted without leading zeros, violates DD.MM.YYYY format",
        "models/fields.py:25",
    ),
}

COL = (50, 55, 34)


def _row(a="", b="", c=""):
    return f"| {a:<{COL[0]}} | {b:<{COL[1]}} | {c:<{COL[2]}} |"


def _divider():
    return f"+{'-' * (COL[0]+2)}+{'-' * (COL[1]+2)}+{'-' * (COL[2]+2)}+"


def build_bug_table(failed_tests: list) -> str:
    known = [(t, *KNOWN_BUGS[t]) for t in failed_tests if t in KNOWN_BUGS]
    unknown = [t for t in failed_tests if t not in KNOWN_BUGS]

    lines = [
        "",
        "=" * 80,
        "BUG SUMMARY",
        "=" * 80,
        "",
        _divider(),
        _row("Failed test", "Bug", "File to fix"),
        _divider(),
    ]

    for test, bug, filepath in known:
        words = bug.split()
        bug_lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 > COL[1]:
                bug_lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        bug_lines.append(cur)

        lines.append(_row(test, bug_lines[0], filepath))
        for extra in bug_lines[1:]:
            lines.append(_row("", extra, ""))
        lines.append(_divider())

    if unknown:
        lines += ["", "Unexpected failures (not in known-bugs map):"]
        for t in unknown:
            lines.append(f"  - {t}")

    lines += [
        "",
        f"Result: {len(failed_tests)} failed  |  {len(known)} known bugs  |  "
        f"{len(unknown)} unexpected",
        "=" * 80,
    ]
    return "\n".join(lines)


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = LOG_DIR / f"test_run_{timestamp}.log"

    print(f"Running tests...  (log -> {log_path})\n")

    project_root = Path(__file__).parent.parent
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=project_root,
    )

    output = proc.stdout + (proc.stderr or "")
    print(output.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))

    failed = []
    for line in output.splitlines():
        if line.startswith("FAILED ") and "::" in line:
            # handles both "file::test_name" and "file::ClassName::test_name"
            test_name = line.split("::")[-1].split(" ")[0]
            if test_name:
                failed.append(test_name)

    header = (
        f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        + "=" * 80 + "\n\n"
    )

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(output)
        if failed:
            f.write(build_bug_table(failed))
            f.write("\n")

    print(f"\nLog saved: {log_path}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
