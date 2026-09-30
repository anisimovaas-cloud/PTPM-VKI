import unittest

from src.my_project import ErrorCode, RegistrationValidator, password_fingerprint


VALID_PASSWORD = "Секрет1!"


class TestRegistrationValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RegistrationValidator()

    def test_accepts_string_login(self):
        result = self.validator.check("student_2026", VALID_PASSWORD, VALID_PASSWORD)
        self.assertTrue(result.success)

    def test_accepts_phone_login(self):
        result = self.validator.check("+7-999-123-4567", VALID_PASSWORD, VALID_PASSWORD)
        self.assertTrue(result.success)

    def test_accepts_email_login(self):
        result = self.validator.check("student.lab@example.com", VALID_PASSWORD, VALID_PASSWORD)
        self.assertTrue(result.success)

    def test_rejects_empty_login(self):
        result = self.validator.check("", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.EMPTY_LOGIN)

    def test_rejects_blacklisted_login_ignoring_case(self):
        result = self.validator.check("ADMIN", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.LOGIN_BLACKLISTED)

    def test_rejects_phone_without_hyphens(self):
        result = self.validator.check("+79991234567", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.INVALID_PHONE)

    def test_rejects_email_without_domain(self):
        result = self.validator.check("student@", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.INVALID_EMAIL)

    def test_rejects_short_username(self):
        result = self.validator.check("abcd", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.SHORT_USERNAME)

    def test_rejects_username_with_hyphen(self):
        result = self.validator.check("student-name", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result.error_code, ErrorCode.INVALID_USERNAME)

    def test_rejects_empty_password(self):
        result = self.validator.check("student", "", "")
        self.assertEqual(result.error_code, ErrorCode.EMPTY_PASSWORD)

    def test_rejects_short_password(self):
        result = self.validator.check("student", "Аб1!", "Аб1!")
        self.assertEqual(result.error_code, ErrorCode.SHORT_PASSWORD)

    def test_rejects_latin_letter_in_password(self):
        result = self.validator.check("student", "СекретA1!", "СекретA1!")
        self.assertEqual(result.error_code, ErrorCode.LATIN_IN_PASSWORD)

    def test_rejects_space_in_password(self):
        result = self.validator.check("student", "Секрет 1!", "Секрет 1!")
        self.assertEqual(result.error_code, ErrorCode.INVALID_PASSWORD_CHAR)

    def test_requires_lowercase_letter(self):
        result = self.validator.check("student", "СЕКРЕТ1!", "СЕКРЕТ1!")
        self.assertEqual(result.error_code, ErrorCode.PASSWORD_NO_LOWER)

    def test_requires_uppercase_letter(self):
        result = self.validator.check("student", "секрет1!", "секрет1!")
        self.assertEqual(result.error_code, ErrorCode.PASSWORD_NO_UPPER)

    def test_requires_digit(self):
        result = self.validator.check("student", "Секрет!!", "Секрет!!")
        self.assertEqual(result.error_code, ErrorCode.PASSWORD_NO_DIGIT)

    def test_requires_special_character(self):
        result = self.validator.check("student", "Секрет12", "Секрет12")
        self.assertEqual(result.error_code, ErrorCode.PASSWORD_NO_SPECIAL)

    def test_rejects_password_confirmation_mismatch(self):
        result = self.validator.check("student", "Секрет1!", "Секрет2!")
        self.assertEqual(result.error_code, ErrorCode.PASSWORD_MISMATCH)

    def test_same_password_has_same_fingerprint(self):
        self.assertEqual(password_fingerprint("Секрет1!"), password_fingerprint("Секрет1!"))

    def test_different_passwords_have_different_fingerprints(self):
        self.assertNotEqual(password_fingerprint("Секрет1!"), password_fingerprint("Секрет2!"))


if __name__ == "__main__":
    unittest.main()
