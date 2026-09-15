import unittest

from validator import ErrorCode, RegistrationValidator, password_fingerprint


GOOD_PASSWORD = "Секрет1!"


class RegistrationValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = RegistrationValidator()

    def assert_error(
        self,
        login: str,
        password: str,
        confirmation: str,
        code: ErrorCode,
    ) -> None:
        result = self.validator.check(login, password, confirmation)
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, code)
        self.assertNotEqual(result.message, "")

    def test_string_login_is_valid(self) -> None:
        result = self.validator.check(
            "student_2026",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.message, "")
        self.assertIsNone(result.error_code)

    def test_phone_login_is_valid(self) -> None:
        result = self.validator.check(
            "+7-999-123-4567",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
        )
        self.assertTrue(result.success)

    def test_email_login_is_valid(self) -> None:
        result = self.validator.check(
            "student.lab@example.com",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
        )
        self.assertTrue(result.success)

    def test_empty_login(self) -> None:
        self.assert_error("", GOOD_PASSWORD, GOOD_PASSWORD, ErrorCode.EMPTY_LOGIN)

    def test_blacklist_is_case_insensitive(self) -> None:
        self.assert_error(
            "ADMIN",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.LOGIN_BLACKLISTED,
        )

    def test_invalid_phone_without_hyphens(self) -> None:
        self.assert_error(
            "+79991234567",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_PHONE,
        )

    def test_invalid_phone_too_short(self) -> None:
        self.assert_error(
            "+7-999-12-4567",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_PHONE,
        )

    def test_invalid_email_without_domain(self) -> None:
        self.assert_error(
            "student@",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_EMAIL,
        )

    def test_invalid_email_without_dot(self) -> None:
        self.assert_error(
            "student@example",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_EMAIL,
        )

    def test_username_too_short(self) -> None:
        self.assert_error(
            "abcd",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.SHORT_USERNAME,
        )

    def test_username_with_cyrillic_is_invalid(self) -> None:
        self.assert_error(
            "студент",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_USERNAME,
        )

    def test_username_with_hyphen_is_invalid(self) -> None:
        self.assert_error(
            "student-name",
            GOOD_PASSWORD,
            GOOD_PASSWORD,
            ErrorCode.INVALID_USERNAME,
        )

    def test_empty_password(self) -> None:
        self.assert_error("student", "", "", ErrorCode.EMPTY_PASSWORD)

    def test_short_password(self) -> None:
        self.assert_error("student", "Аб1!", "Аб1!", ErrorCode.SHORT_PASSWORD)

    def test_latin_character_in_password(self) -> None:
        self.assert_error(
            "student",
            "СекретA1!",
            "СекретA1!",
            ErrorCode.LATIN_IN_PASSWORD,
        )

    def test_space_in_password(self) -> None:
        self.assert_error(
            "student",
            "Секрет 1!",
            "Секрет 1!",
            ErrorCode.INVALID_PASSWORD_CHAR,
        )

    def test_emoji_in_password(self) -> None:
        self.assert_error(
            "student",
            "Секрет1!🙂",
            "Секрет1!🙂",
            ErrorCode.INVALID_PASSWORD_CHAR,
        )

    def test_no_lowercase_letter(self) -> None:
        self.assert_error(
            "student",
            "СЕКРЕТ1!",
            "СЕКРЕТ1!",
            ErrorCode.PASSWORD_NO_LOWER,
        )

    def test_no_uppercase_letter(self) -> None:
        self.assert_error(
            "student",
            "секрет1!",
            "секрет1!",
            ErrorCode.PASSWORD_NO_UPPER,
        )

    def test_no_digit(self) -> None:
        self.assert_error(
            "student",
            "Секрет!!",
            "Секрет!!",
            ErrorCode.PASSWORD_NO_DIGIT,
        )

    def test_no_special_character(self) -> None:
        self.assert_error(
            "student",
            "Секрет12",
            "Секрет12",
            ErrorCode.PASSWORD_NO_SPECIAL,
        )

    def test_confirmation_mismatch(self) -> None:
        self.assert_error(
            "student",
            "Секрет1!",
            "Секрет2!",
            ErrorCode.PASSWORD_MISMATCH,
        )

    def test_same_password_has_same_fingerprint(self) -> None:
        self.assertEqual(
            password_fingerprint("Секрет1!"),
            password_fingerprint("Секрет1!"),
        )

    def test_different_password_has_different_fingerprint(self) -> None:
        self.assertNotEqual(
            password_fingerprint("Секрет1!"),
            password_fingerprint("Секрет2!"),
        )

    def test_fingerprint_does_not_reveal_password(self) -> None:
        password = "Секрет1!"
        self.assertNotIn(password, password_fingerprint(password))


if __name__ == "__main__":
    unittest.main()
