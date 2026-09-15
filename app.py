from logging_setup import build_logger
from validator import RegistrationValidator


def main() -> None:
    logger = build_logger()
    validator = RegistrationValidator(logger)

    logger.info("Запуск программы проверки регистрации")

    try:
        login = input("Логин: ")
        password = input("Пароль: ")
        confirmation = input("Подтверждение пароля: ")

        result = validator.check(
            login=login,
            password=password,
            confirmation=confirmation,
        )

        print(result.success)
        print(result.message)
    except (EOFError, KeyboardInterrupt):
        logger.warning("Ввод пользователя был прерван")
        print(False)
        print("Ввод данных был прерван.")
    except Exception:
        logger.exception("Критическая необработанная ошибка")
        print(False)
        print("Внутренняя ошибка приложения.")
    finally:
        logger.info("Завершение программы")


if __name__ == "__main__":
    main()
