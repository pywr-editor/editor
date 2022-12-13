from dataclasses import dataclass


@dataclass
class FormValidation:
    validation: bool
    error_message: str | None = None
