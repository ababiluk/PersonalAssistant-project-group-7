# Running Automated Tests

## Requirements

- Python 3.10+
- pytest

Install pytest if not already installed:

```
pip install pytest
```

---

## One-command run (recommended)

Runs all tests, prints results, and saves a timestamped log automatically:

```
python tests/run_tests.py
```

The log is saved to `tests/logs/test_run_YYYY-MM-DD_HH-MM-SS.log` and includes:
- Full pytest output
- Bug summary table at the end (for any known failing tests)

---

## Manual pytest commands

Run all tests:
```
python -m pytest tests/ -v
```

Run a single test file:
```
python -m pytest tests/test_models.py -v
python -m pytest tests/test_handlers.py -v
python -m pytest tests/test_validation.py -v
```

Run a single test by name:
```
python -m pytest tests/ -v -k "test_phone_valid"
```

Run only failing tests from the last run:
```
python -m pytest tests/ --lf
```

---

## Test files

| File | What it covers |
|---|---|
| `tests/test_models.py` | `Phone`, `Birthday`, `Record`, `AddressBook` |
| `tests/test_handlers.py` | All command handlers + `parse_input`, `save_data`, `load_data` |
| `tests/test_validation.py` | Input validation edge cases for each field |
| `tests/test_notes.py` | `Note` field, `Record` note methods, all note handlers |

---

## Log files

All logs are stored in `tests/logs/`.
Each run creates a new file named `test_run_YYYY-MM-DD_HH-MM-SS.log`.
If any tests fail, a bug summary table is appended at the end of the log.

---

## Known failing tests

These tests intentionally fail to document real bugs in the code:

| Test | Bug |
|---|---|
| `test_add_contact_name_with_space` | `isalpha()` rejects names with spaces |
| `test_birthdays_no_upcoming/with_upcoming` | `birthdays()` has wrong signature |
| `test_birthday_impossible_date` | Misleading error message for impossible dates |
| `test_record_str_no_phones` | Empty phones field in `__str__` output |
| `test_unicode_digits` | `Phone` accepts non-ASCII digits |
| `test_no_leading_zero` | `Birthday` accepts `1.1.2000` without leading zeros |
