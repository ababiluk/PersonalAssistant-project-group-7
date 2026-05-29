from collections import UserDict
from datetime import date, timedelta


class AddressBook(UserDict):
    # Add a new contact record to the address book
    def add_record(self, record):
        self.data[record.name.value] = record

    # Find a contact by name
    def find(self, name):
        return self.data.get(name)

    # Delete a contact from the address book
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Return birthdays occurring within the specified number of days
    def get_upcoming_birthdays(self, days=7):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday_this_year = record.birthday.value.replace(
                year=today.year
            )  # changing year to current to compare only days

            if birthday_this_year < today:  # moving past birthdays to next year
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until = (birthday_this_year - today).days  # main calculation

            if 0 <= days_until <= days:  # weekends checks
                if birthday_this_year.weekday() == 5:
                    congrats_date = birthday_this_year + timedelta(days=2)
                elif birthday_this_year.weekday() == 6:
                    congrats_date = birthday_this_year + timedelta(days=1)
                else:
                    congrats_date = birthday_this_year

                upcoming.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming
