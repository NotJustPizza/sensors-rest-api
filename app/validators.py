from typing import Any
from email_validator import validate_email, EmailNotValidError
from tortoise.exceptions import ValidationError
from tortoise.validators import Validator


class EmailValidator(Validator):
    allow_smtputf8: bool = True
    allow_empty_local: bool = False
    check_deliverability: bool = False
    test_environment: bool = False
    globally_deliverable: bool = True

    def __call__(self, value: Any):
        try:
            validate_email(
                value,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
                check_deliverability=self.check_deliverability,
                test_environment=self.test_environment,
                globally_deliverable=self.globally_deliverable,
            )
        except EmailNotValidError:
            raise ValidationError(f"Value {value!r} is not valid email address.")
