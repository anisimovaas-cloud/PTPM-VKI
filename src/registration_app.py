import sqlite3
from abc import ABC, abstractmethod

from .my_project import RegistrationValidator as PreviousRegistrationValidator


class RegistrationValidator:
    def validate(self, login, password, password_confirmation):
        result = PreviousRegistrationValidator().check(
            login, password, password_confirmation
        )
        return result.success, result.message


class RegistrationDatabase:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS registrations ("
            "login TEXT, password TEXT, confirmation TEXT, result INTEGER, error TEXT, "
            "PRIMARY KEY (login, password, confirmation))"
        )

    def get(self, login, password, password_confirmation):
        return self.connection.execute(
            "SELECT result, error FROM registrations "
            "WHERE login=? AND password=? AND confirmation=?",
            (login, password, password_confirmation),
        ).fetchone()

    def add(self, login, password, password_confirmation, result, error):
        self.connection.execute(
            "INSERT OR REPLACE INTO registrations VALUES (?, ?, ?, ?, ?)",
            (login, password, password_confirmation, int(result), error),
        )
        self.connection.commit()

    def delete(self, login, password, password_confirmation):
        self.connection.execute(
            "DELETE FROM registrations WHERE login=? AND password=? AND confirmation=?",
            (login, password, password_confirmation),
        )
        self.connection.commit()

    def close(self):
        self.connection.close()


class UserInterface(ABC):
    @abstractmethod
    def get_data(self):
        pass


class ConsoleUserInterface(UserInterface):
    def get_data(self):
        return tuple(
            input(prompt)
            for prompt in ("Введите логин: ", "Введите пароль: ", "Повторите пароль: ")
        )


class ExternalService(ABC):
    @abstractmethod
    def send(self, message):
        pass


class SimulatedExternalService(ExternalService):
    def send(self, message):
        return True


class Controller:
    def __init__(self, user_interface, database, validator, external_service):
        self.user_interface = user_interface
        self.database = database
        self.validator = validator
        self.external_service = external_service

    def run(self):
        login, password, password_confirmation = self.user_interface.get_data()
        cached = self.database.get(login, password, password_confirmation)

        if cached is None:
            result, error = self.validator.validate(
                login, password, password_confirmation
            )
            self.database.add(
                login, password, password_confirmation, result, error
            )
        else:
            result, error = bool(cached[0]), cached[1]

        message = "Регистрация успешна" if result else error
        self.external_service.send(message)
        return message


def main(database_path="registrations.db"):
    database = RegistrationDatabase(database_path)
    try:
        controller = Controller(
            ConsoleUserInterface(),
            database,
            RegistrationValidator(),
            SimulatedExternalService(),
        )
        return controller.run()
    finally:
        database.close()


if __name__ == "__main__":
    print(main())
