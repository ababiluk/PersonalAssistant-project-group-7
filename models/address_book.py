from collections import UserDict
from datetime import date, timedelta


def _occurrence(birthday, year):
    # Map a birthday onto a given year for the upcoming-birthday comparison.
    # Feb 29 has no counterpart in non-leap years, so fall back to Feb 28 instead
    # of crashing the whole command with a ValueError.
    try:
        return birthday.replace(year=year)
    except ValueError:
        return date(year, 2, 28)


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        # Case-insensitive lookup so "john" finds "John". Names are unique
        # ignoring case (stored title-cased), so the first match is the one.
        name_lower = name.lower()
        for record in self.data.values():
            if record.name.value.lower() == name_lower:
                return record
        return None

    def delete(self, name):
        # Match find()'s case-insensitivity so deletion works with any casing.
        record = self.find(name)
        if record:
            del self.data[record.name.value]

    def get_upcoming_birthdays(self, days=7):
        # Find contacts to congratulate within the next `days` days.
        # Accepts the look-ahead window in days. Returns a list of
        # {"name", "congratulation_date" (DD.MM.YYYY)} dicts, where birthdays
        # landing on a weekend are moved to the following Monday.
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            # Compare on this year's date so only month/day matter, not the year born.
            birthday_this_year = _occurrence(record.birthday.value, today.year)

            # Already passed this year -> the next occurrence is next year.
            if birthday_this_year < today:
                birthday_this_year = _occurrence(record.birthday.value, today.year + 1)

            days_until = (birthday_this_year - today).days

            if 0 <= days_until <= days:
                # Weekend birthdays are greeted on the next working day (Monday).
                if birthday_this_year.weekday() == 5:
                    congrats_date = birthday_this_year + timedelta(days=2)
                elif birthday_this_year.weekday() == 6:
                    congrats_date = birthday_this_year + timedelta(days=1)
                else:
                    congrats_date = birthday_this_year

                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congrats_date.strftime("%d.%m.%Y"),
                })

        return upcoming
