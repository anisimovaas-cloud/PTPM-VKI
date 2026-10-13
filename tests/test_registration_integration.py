import unittest
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from src.registration_app import (
    ConsoleUserInterface,
    Controller,
    main,
    RegistrationDatabase,
    RegistrationValidator,
    SimulatedExternalService,
)


class RegistrationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.database = RegistrationDatabase()

    def tearDown(self):
        self.database.close()

    def test_valid_registration_uses_input_database_and_service(self):
        service = Mock()
        controller = Controller(
            ConsoleUserInterface(),
            self.database,
            RegistrationValidator(),
            service,
        )
        with patch(
            "builtins.input",
            side_effect=["student_1", "Пароль1!", "Пароль1!"],
        ) as user_input:
            result = controller.run()

        self.assertEqual(result, "Регистрация успешна")
        self.assertEqual(user_input.call_count, 3)
        service.send.assert_called_once_with(result)
        self.assertEqual(
            self.database.get("student_1", "Пароль1!", "Пароль1!"),
            (1, ""),
        )

    def test_cached_result_skips_validation_and_is_sent(self):
        user = Mock()
        user.get_data.return_value = ("student_1", "Пароль1!", "Пароль1!")
        validator = Mock()
        service = Mock()
        self.database.add("student_1", "Пароль1!", "Пароль1!", True, "")
        controller = Controller(user, self.database, validator, service)

        result = controller.run()

        self.assertEqual(result, "Регистрация успешна")
        validator.validate.assert_not_called()
        service.send.assert_called_once_with(result)

    def test_invalid_registration_is_saved_and_sent(self):
        user = Mock()
        user.get_data.return_value = ("admin", "Пароль1!", "Пароль1!")
        service = Mock()
        controller = Controller(
            user, self.database, RegistrationValidator(), service
        )

        result = controller.run()

        self.assertIn("черном списке", result)
        self.assertEqual(
            self.database.get("admin", "Пароль1!", "Пароль1!"),
            (0, result),
        )
        service.send.assert_called_once_with(result)

    def test_database_add_get_and_delete(self):
        self.assertIsNone(self.database.get("student_1", "Пароль1!", "Пароль1!"))
        self.database.add("student_1", "Пароль1!", "Пароль1!", False, "ошибка")
        self.assertEqual(
            self.database.get("student_1", "Пароль1!", "Пароль1!"),
            (0, "ошибка"),
        )
        self.database.delete("student_1", "Пароль1!", "Пароль1!")
        self.assertIsNone(self.database.get("student_1", "Пароль1!", "Пароль1!"))

    def test_console_interface_reads_three_fields(self):
        with patch("builtins.input", side_effect=["login", "pass", "pass"]) as user_input:
            result = ConsoleUserInterface().get_data()

        self.assertEqual(result, ("login", "pass", "pass"))
        self.assertEqual(user_input.call_count, 3)

    def test_simulated_service(self):
        self.assertTrue(SimulatedExternalService().send("Регистрация успешна"))

    def test_main_runs_registration_flow(self):
        with TemporaryDirectory() as directory:
            with patch(
                "builtins.input",
                side_effect=["student_1", "Пароль1!", "Пароль1!"],
            ):
                result = main(f"{directory}/registrations.db")

        self.assertEqual(result, "Регистрация успешна")


if __name__ == "__main__":
    unittest.main()
