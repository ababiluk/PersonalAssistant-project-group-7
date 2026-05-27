"""
Валидация некорректных данных для каждого поля.
Тесты с пометкой BUG ожидают правильное поведение и ПАДАЮТ — указывая на баг в коде.
"""
import pytest
from models.fields import Phone, Birthday


# =============================================================================
# Phone — ровно 10 цифр, только ASCII-цифры
# =============================================================================

class TestPhoneValidation:

    def test_valid(self):
        assert Phone("1234567890").value == "1234567890"

    def test_exactly_10_zeros(self):
        assert Phone("0000000000").value == "0000000000"

    # --- неверная длина ---

    def test_empty(self):
        with pytest.raises(ValueError):
            Phone("")

    def test_too_short_9(self):
        with pytest.raises(ValueError):
            Phone("123456789")

    def test_too_long_11(self):
        with pytest.raises(ValueError):
            Phone("12345678901")

    def test_single_digit(self):
        with pytest.raises(ValueError):
            Phone("1")

    # --- нецифровые символы ---

    def test_letters_only(self):
        with pytest.raises(ValueError):
            Phone("abcdefghij")

    def test_mixed_digits_letters(self):
        with pytest.raises(ValueError):
            Phone("123456789a")

    def test_with_spaces(self):
        with pytest.raises(ValueError):
            Phone("123 456 789")

    def test_with_dashes(self):
        with pytest.raises(ValueError):
            Phone("123-456-789")

    def test_with_plus(self):
        with pytest.raises(ValueError):
            Phone("+1234567890")

    def test_with_parentheses(self):
        with pytest.raises(ValueError):
            Phone("(123)456789")

    def test_with_dots(self):
        with pytest.raises(ValueError):
            Phone("123.456.789")

    def test_special_chars(self):
        with pytest.raises(ValueError):
            Phone("!@#$%^&*()")

    def test_newline(self):
        with pytest.raises(ValueError):
            Phone("123456789\n")

    def test_tab(self):
        with pytest.raises(ValueError):
            Phone("123456789\t")

    # BUG: isdigit() возвращает True для арабских/юникодных цифр — должны отклоняться
    def test_unicode_digits(self):
        with pytest.raises(ValueError):
            Phone("١٢٣٤٥٦٧٨٩٠")  # 10 арабских цифр — падает: код принимает их


# =============================================================================
# Birthday — формат DD.MM.YYYY, реальная дата
# =============================================================================

class TestBirthdayValidation:

    def test_valid(self):
        from datetime import date
        assert Birthday("15.06.1990").value == date(1990, 6, 15)

    def test_leap_year_valid(self):
        from datetime import date
        assert Birthday("29.02.2000").value == date(2000, 2, 29)

    def test_first_day_of_year(self):
        from datetime import date
        assert Birthday("01.01.1900").value == date(1900, 1, 1)

    def test_last_day_of_year(self):
        from datetime import date
        assert Birthday("31.12.2099").value == date(2099, 12, 31)

    # --- неверные разделители ---

    def test_iso_format(self):
        with pytest.raises(ValueError):
            Birthday("2000-01-15")

    def test_slash_separator(self):
        with pytest.raises(ValueError):
            Birthday("15/01/2000")

    def test_space_separator(self):
        with pytest.raises(ValueError):
            Birthday("15 01 2000")

    def test_no_separator(self):
        with pytest.raises(ValueError):
            Birthday("15012000")

    def test_year_first(self):
        with pytest.raises(ValueError):
            Birthday("2000.01.15")

    # --- несуществующие даты ---

    def test_february_30(self):
        with pytest.raises(ValueError):
            Birthday("30.02.2000")

    def test_february_29_non_leap(self):
        with pytest.raises(ValueError):
            Birthday("29.02.2001")

    def test_april_31(self):
        with pytest.raises(ValueError):
            Birthday("31.04.2000")

    def test_month_0(self):
        with pytest.raises(ValueError):
            Birthday("15.00.2000")

    def test_month_13(self):
        with pytest.raises(ValueError):
            Birthday("15.13.2000")

    def test_day_0(self):
        with pytest.raises(ValueError):
            Birthday("00.01.2000")

    def test_day_32(self):
        with pytest.raises(ValueError):
            Birthday("32.01.2000")

    # --- нечисловые значения ---

    def test_empty(self):
        with pytest.raises(ValueError):
            Birthday("")

    def test_letters(self):
        with pytest.raises(ValueError):
            Birthday("ab.cd.efgh")

    def test_partial_date(self):
        with pytest.raises(ValueError):
            Birthday("15.01")

    def test_extra_parts(self):
        with pytest.raises(ValueError):
            Birthday("15.01.2000.extra")

    # BUG: strptime принимает "1.1.2000" без ведущих нулей, хотя формат DD.MM.YYYY
    def test_no_leading_zero(self):
        with pytest.raises(ValueError):
            Birthday("1.1.2000")  # падает: код принимает без ведущего нуля
