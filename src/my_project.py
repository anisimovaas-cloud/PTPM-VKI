from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import string
from dataclasses import dataclass
from enum import Enum


PHONE_PATTERN = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
CYRILLIC_LOWER_PATTERN = re.compile(r"[а-яё]")
CYRILLIC_UPPER_PATTERN = re.compile(r"[А-ЯЁ]")
LATIN_PATTERN = re.compile(r"[A-Za-z]")
DIGIT_PATTERN = re.compile(r"\d")

BLACKLIST = frozenset(
    {"admin", "administrator", "root", "support", "test", "user", "system", "qwerty"}
)

SPECIAL_CHARACTERS = frozenset(string.punctuation)


class ErrorCode(str, Enum):
    EMPTY_LOGIN = "EMPTY_LOGIN"
    LOGIN_BLACKLISTED = "LOGIN_BLACKLISTED"
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_EMAIL = "INVALID_EMAIL"
    SHORT_USERNAME = "SHORT_USERNAME"
    INVALID_USERNAME = "INVALID_USERNAME"
    EMPTY_PASSWORD = "EMPTY_PASSWORD"
    SHORT_PASSWORD = "SHORT_PASSWORD"
    LATIN_IN_PASSWORD = "LATIN_IN_PASSWORD"
    INVALID_PASSWORD_CHAR = "INVALID_PASSWORD_CHAR"
    PASSWORD_NO_LOWER = "PASSWORD_NO_LOWER"
    PASSWORD_NO_UPPER = "PASSWORD_NO_UPPER"
    PASSWORD_NO_DIGIT = "PASSWORD_NO_DIGIT"
    PASSWORD_NO_SPECIAL = "PASSWORD_NO_SPECIAL"
    PASSWORD_MISMATCH = "PASSWORD_MISMATCH"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.EMPTY_LOGIN: "Логин не может быть пустым.",
    ErrorCode.LOGIN_BLACKLISTED: "Логин находится в черном списке.",
    ErrorCode.INVALID_PHONE: "Номер телефона должен иметь формат +x-xxx-xxx-xxxx.",
    ErrorCode.INVALID_EMAIL: "Некорректный адрес электронной почты.",
    ErrorCode.SHORT_USERNAME: "Строковый логин должен содержать минимум 5 символов.",
    ErrorCode.INVALID_USERNAME: "Строковый логин может содержать только латинские буквы, цифры и '_'.",
    ErrorCode.EMPTY_PASSWORD: "Пароль не может быть пустым.",
    ErrorCode.SHORT_PASSWORD: "Пароль должен содержать минимум 7 символов.",
    ErrorCode.LATIN_IN_PASSWORD: "Пароль не должен содержать латинские буквы.",
    ErrorCode.INVALID_PASSWORD_CHAR: (
        "В пароле разрешены только кириллица, цифры и специальные символы; пробелы запрещены."
    ),
    ErrorCode.PASSWORD_NO_LOWER: "В пароле должна быть хотя бы одна строчная кириллическая буква.",
    ErrorCode.PASSWORD_NO_UPPER: "В пароле должна быть хотя бы одна заглавная кириллическая буква.",
    ErrorCode.PASSWORD_NO_DIGIT: "В пароле должна быть хотя бы одна цифра.",
    ErrorCode.PASSWORD_NO_SPECIAL: "В пароле должен быть хотя бы один специальный символ.",
    ErrorCode.PASSWORD_MISMATCH: "Пароль и его подтверждение не совпадают.",
    ErrorCode.INTERNAL_ERROR: "Внутренняя ошибка при проверке данных.",
}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    success: bool
    message: str = ""
    error_code: ErrorCode | None = None


class ValidationError(Exception):
    def __init__(self, code: ErrorCode) -> None:
        self.code = code
        super().__init__(ERROR_MESSAGES[code])


def password_fingerprint(password: str) -> str:
    key = os.getenv(
        "PTPM_LOG_SECRET",
        "lab-1-alternative-local-secret",
    ).encode("utf-8")

    digest = hmac.new(
        key=key,
        msg=password.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"pwd#{digest[:18]}"


class RegistrationValidator:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger

    def check(self, login: str, password: str, confirmation: str) -> ValidationResult:
        self._log_request(login, password, confirmation)

        try:
            self._check_login(login)
            self._check_password(password)

            if password != confirmation:
                raise ValidationError(ErrorCode.PASSWORD_MISMATCH)

        except ValidationError as exc:
            result = ValidationResult(
                success=False,
                message=ERROR_MESSAGES[exc.code],
                error_code=exc.code,
            )
            self._log_result(login, password, confirmation, result)
            return result

        except Exception:
            if self.logger is not None:
                self.logger.exception(
                    "Неожиданная ошибка валидации | login=%r | password=%s",
                    login,
                    password_fingerprint(password),
                )

            return ValidationResult(
                success=False,
                message=ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR],
                error_code=ErrorCode.INTERNAL_ERROR,
            )

        result = ValidationResult(success=True)
        self._log_result(login, password, confirmation, result)
        return result

    @staticmethod
    def _check_login(login: str) -> None:
        if login == "":
            raise ValidationError(ErrorCode.EMPTY_LOGIN)

        if login.casefold() in BLACKLIST:
            raise ValidationError(ErrorCode.LOGIN_BLACKLISTED)

        if login.startswith("+"):
            if not PHONE_PATTERN.fullmatch(login):
                raise ValidationError(ErrorCode.INVALID_PHONE)
            return

        if "@" in login:
            if not EMAIL_PATTERN.fullmatch(login):
                raise ValidationError(ErrorCode.INVALID_EMAIL)
            return

        if len(login) < 5:
            raise ValidationError(ErrorCode.SHORT_USERNAME)

        if not USERNAME_PATTERN.fullmatch(login):
            raise ValidationError(ErrorCode.INVALID_USERNAME)

    @staticmethod
    def _check_password(password: str) -> None:
        if password == "":
            raise ValidationError(ErrorCode.EMPTY_PASSWORD)

        if len(password) < 7:
            raise ValidationError(ErrorCode.SHORT_PASSWORD)

        if LATIN_PATTERN.search(password):
            raise ValidationError(ErrorCode.LATIN_IN_PASSWORD)

        if not RegistrationValidator._all_password_chars_allowed(password):
            raise ValidationError(ErrorCode.INVALID_PASSWORD_CHAR)

        if not CYRILLIC_LOWER_PATTERN.search(password):
            raise ValidationError(ErrorCode.PASSWORD_NO_LOWER)

        if not CYRILLIC_UPPER_PATTERN.search(password):
            raise ValidationError(ErrorCode.PASSWORD_NO_UPPER)

        if not DIGIT_PATTERN.search(password):
            raise ValidationError(ErrorCode.PASSWORD_NO_DIGIT)

        if not any(char in SPECIAL_CHARACTERS for char in password):
            raise ValidationError(ErrorCode.PASSWORD_NO_SPECIAL)

    @staticmethod
    def _all_password_chars_allowed(password: str) -> bool:
        for char in password:
            if char.isspace():
                return False
            if char.isdigit():
                continue
            if char in SPECIAL_CHARACTERS:
                continue
            if ("а" <= char <= "я") or ("А" <= char <= "Я") or char in {"ё", "Ё"}:
                continue
            return False
        return True

    def _log_request(self, login: str, password: str, confirmation: str) -> None:
        if self.logger is None:
            return
        self.logger.debug(
            "Входные данные | login=%r | password=%s | confirmation=%s",
            login,
            password_fingerprint(password),
            password_fingerprint(confirmation),
        )

    def _log_result(
        self,
        login: str,
        password: str,
        confirmation: str,
        result: ValidationResult,
    ) -> None:
        if self.logger is None:
            return

        if result.success:
            self.logger.info(
                "Проверка успешна | login=%r | password=%s | confirmation=%s | result=True",
                login,
                password_fingerprint(password),
                password_fingerprint(confirmation),
            )
            return

        self.logger.warning(
            "Проверка отклонена | login=%r | password=%s | confirmation=%s | result=False | code=%s | reason=%s",
            login,
            password_fingerprint(password),
            password_fingerprint(confirmation),
            result.error_code.value if result.error_code else "UNKNOWN",
            result.message,
        )
