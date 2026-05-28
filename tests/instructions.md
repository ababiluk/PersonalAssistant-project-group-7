# Running Tests

## Requirements

- Python 3.10+
- pytest

```bash
pip install pytest
```

---

## One command (recommended)

Runs all tests, prints results to the console, and saves a timestamped log automatically:

```bash
python tests/run_tests.py
```

Log is saved to `tests/logs/test_run_YYYY-MM-DD_HH-MM-SS.log`.

---

## Direct pytest commands

Run all tests:
```bash
python -m pytest tests/ -v
```

Run a single file:
```bash
python -m pytest tests/test_fields.py -v
python -m pytest tests/test_commands.py -v
python -m pytest tests/test_e2e.py -v
```

Other useful flags:

| Flag | Effect |
|---|---|
| `-k "test_phone"` | Run only tests whose name matches the pattern |
| `--lf` | Re-run only tests that failed last time |
| `-x` | Stop after the first failure |
| `--tb=short` | Shorter traceback on failures |
| `-q` | Minimal output — names + summary only |

---

## Test files

| File | What it covers |
|---|---|
| `test_fields.py` | Field-level validation: `Phone`, `Birthday`, `Email`, `Note`, `Name`, `Address` |
| `test_commands.py` | `Record` and `AddressBook` models, all 23 command handlers, input parsing, persistence |
| `test_e2e.py` | Full session: empty book -> add contacts -> all commands -> save/reload |

---

## Understanding xfail

Tests marked `@pytest.mark.xfail` document **known bugs**.
pytest reports them as `xfailed` — the suite stays green while bugs are tracked.

```
xfailed  — expected failure, bug not yet fixed
xpassed  — test unexpectedly passed (bug was fixed — remove the xfail marker)
```

### Current known bugs

| Test | Bug |
|---|---|
| `TestPhoneField::test_plus_prefix_rejected` | `Phone("+1234567890")` strips `+` and accepts the number |
| `TestPhoneField::test_unicode_arabic_digits_rejected` | `isdigit()` accepts Arabic-Indic digits |
| `TestBirthdayField::test_no_leading_zero_rejected` | `Birthday("1.1.2000")` accepted without leading zeros |
| `TestNoteCommands::test_edit_note_preserves_tags` | `edit_note` replaces the `Note` object, losing all tags |
| `TestNameField::test_empty_name_raises` | `Name("")` accepted — no field-level validation |
| `TestNameField::test_whitespace_only_name_raises` | `Name("   ")` accepted — no field-level validation |
| `TestNameField::test_non_letter_name_raises` | `Name("Alice123")` accepted — no field-level validation |
| `TestAddressField::test_empty_address_raises` | `Address("")` accepted — no field-level validation |
| `TestAddressField::test_whitespace_only_address_raises` | `Address("   ")` accepted — no field-level validation |
