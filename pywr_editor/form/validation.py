from dataclasses import dataclass


@dataclass
class Validation:
    error_message: str | None = None
    """ The error message. If the message is provided, the form validation is flagged
    as failed """

    def __post_init__(self):
        """
        Store the validation status in the self.validation flag.
        :return:
        """
        if self.error_message is None:
            self.validation = True
        else:
            self.validation = False
